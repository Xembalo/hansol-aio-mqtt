from typing import TYPE_CHECKING
import requests
from bs4 import BeautifulSoup
import time
import pymysql
import paho.mqtt.client as mqtt
import json
import sys
import argparse


#Read Table Cell next to a given cell by its content
def findValue(soup, caption):
    return soup.find(string=caption).parent.next_sibling.contents[0].strip()

#Read general information
def readDeviceInfo(session):
    response = session.get("http://" + ESS_HOST + ":21710/f0")
    soup = BeautifulSoup(response.text, features="html.parser")

    model = findValue(soup, "EMS-Model Name")
    sw_version = findValue(soup, "EMS Version")

    response = session.get("http://" + ESS_HOST + ":21710/f8")
    soup = BeautifulSoup(response.text, features="html.parser")

    sn = findValue(soup, "S-Number")

    return model, sw_version, sn

#Read contents from qhome-stats-page
def readStats(session):
    
    response = session.get("http://" + ESS_HOST + ":21710/f8")
    soup = BeautifulSoup(response.text, features="html.parser")

    battery = float(findValue(soup, "BT_SOC"))
    pv1 = float(findValue(soup, "PV_1_P(30s)"))
    pv2 = float(findValue(soup, "PV_2_P(30s)"))
    grid = float(findValue(soup, "GRID_P(30s)"))
    temp = float(findValue(soup, "Temp"))
    load = float(findValue(soup, "LOAD_P(30s)"))

    if grid >= 0:
        demand = grid
        feedin = 0
    else:
        demand = 0
        feedin = grid * -1

    return battery, pv1, pv2, demand, feedin, load, temp

def calcStats(session):
    #Read values from stat page
    battery1, pv11, pv21, demand1, feedin1, consumption1, temp1 = readStats(session)

    #wait 31 seconds, qhome avg over 30 seconds
    time.sleep(31)

    #Read next stats
    battery2, pv12, pv22, demand2, feedin2, consumption2, temp2 = readStats(session)

    #calc avg values
    batteryavg = (battery1 + battery2)/2
    tempavg = (temp1 + temp2)/2
    pv1avg = (pv11 + pv12)/2000
    pv2avg = (pv21 + pv22)/2000
    demandgridavg = (demand1 + demand2)/2000
    feedingridavg = (feedin1 + feedin2)/2000
    consumptionavg = (consumption1 + consumption2)/2000
    
    #calc battery feedin or demand
    if pv1avg + pv2avg + demandgridavg > feedingridavg + consumptionavg:
        demandbatteryavg = 0
        feedinbatteryavg = pv1avg + pv2avg + demandgridavg - feedingridavg - consumptionavg
    else:
        feedinbatteryavg = 0
        demandbatteryavg = consumptionavg + feedingridavg - pv1avg - pv2avg - demandgridavg
    
    return batteryavg, pv1avg, pv2avg, demandgridavg, feedingridavg, consumptionavg, tempavg, feedinbatteryavg, demandbatteryavg

def insertIntoMariadb(logdate, battery, pv1, pv2, demand, feedin, consumption, temp):
    conn  = pymysql.connect(
                host=MARIADB_HOST, 
                user=MARIADB_USER, 
                password=MARIADB_PASS, 
                database=MARIADB_DATABASE,
                port = MARIADB_PORT
                )
    
    # Create a cursor object
    cur  = conn.cursor()
    pv = pv1 + pv2

    query = f"INSERT INTO logs (date, demand, feedin, consumption, battery_percent, pv, pv1, pv2, temperature) VALUES ('{logdate}', '{demand}', '{feedin}', '{consumption}', '{battery}', '{pv}', '{pv1}', '{pv2}', '{temp}')"
    
    cur.execute(query)
    conn.commit()
    conn.close()

#push auto discovery info for home assistant
def pushMqttConfig(mqttclient, model_name, sn, sw_version):
    
    data = {}
    data["device"] = {}
    data["device"]["manufacturer"] = "Samsung"
    data["device"]["model"] = model_name
    data["device"]["name"] = "ESS 5.5 AiO"
    data["device"]["identifiers"] = [sn]
    data["device"]["sw_version"] = sw_version

    data["name"] = "Batterie"
    data["unique_id"] = MQTT_TOPIC + "_battery"
    data["device_class"] = "battery"
    data["unit_of_measurement"] = "%"
    data["state_topic"] = MQTT_TOPIC + "/state"
    data["value_template"] = "{{ value_json.battery}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)
    
    data["name"] = "Photovoltaik 1"
    data["unique_id"] = MQTT_TOPIC + "_pv1"
    data["device_class"] = "energy"
    data["state_class"] = "measurement"
    data["unit_of_measurement"] = "kWh"
    data["icon"] = "mdi:solar-power"
    data["value_template"] = "{{ value_json.pv1}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Photovoltaik 2"
    data["unique_id"] = MQTT_TOPIC + "_pv2"
    data["value_template"] = "{{ value_json.pv2}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Entnahme vom Netz"
    data["unique_id"] = MQTT_TOPIC + "_demand_grid"
    del data['icon']
    data["value_template"] = "{{ value_json.demandgrid}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Einspeisung ins Netz"
    data["unique_id"] = MQTT_TOPIC + "_feedin_grid"
    data["value_template"] = "{{ value_json.feedingrid}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Hausverbrauch"
    data["unique_id"] = MQTT_TOPIC + "_consumption"
    data["value_template"] = "{{ value_json.consumption}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)
   
    data["name"] = "Entnahme aus Batterie"
    data["unique_id"] = MQTT_TOPIC + "_demand_battery"
    data["value_template"] = "{{ value_json.demandbattery}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Einspeisung in Batterie"
    data["unique_id"] = MQTT_TOPIC + "_feedin_battery"
    data["value_template"] = "{{ value_json.feedinbattery}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

    data["name"] = "Temperatur"
    data["unique_id"] = MQTT_TOPIC + "_temperature"
    data["device_class"] = "temperature"
    data["unit_of_measurement"] = "°C"
    data["state_topic"] = MQTT_TOPIC + "/state"
    data["value_template"] = "{{ value_json.temperature}}"
    mqttclient.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS, retain=True)

def pushMqttStats(mqttclient, logdate, battery, pv1, pv2, demandgrid, feedingrid, consumption, temp, feedinbattery, demandbattery):  
    data = {}
    data["date"] = logdate
    data["battery"] = battery
    data["pv"] = round(pv1 + pv2, 3)
    data["pv1"] = round(pv1, 3)
    data["pv2"] = round(pv2, 3)
    data["demandgrid"] = round(demandgrid, 3)
    data["feedingrid"] = round(feedingrid, 3)
    data["consumption"] = round(consumption, 3)
    data["feedinbattery"] = round(feedinbattery, 3)
    data["demandbattery"] = round(demandbattery, 3)
    data["temperature"] = round(temp, 1)    
    
    mqttclient.publish(MQTT_TOPIC + "/state", json.dumps(data), qos=MQTT_QOS)

def main():
    global ESS_HOST
    global MARIADB_ENABLED
    global MARIADB_HOST
    global MARIADB_PORT
    global MARIADB_USER
    global MARIADB_PASS
    global MARIADB_DATABASE
    global MQTT_ENABLED
    global MQTT_CLIENT_IDENTIFIER
    global MQTT_TOPIC
    global MQTT_BROKER_ADDRESS
    global MQTT_PORT
    global MQTT_QOS
    global MQTT_USER
    global MQTT_PASS
    global MQTT_FORCE_CONFIG_BROADCAST

    parser = argparse.ArgumentParser(
            description="Reads stats from Samsung AIO ESS 5.5 web inteface and push to Database and/or MQTT", 
            epilog="Report bugs, comments or improvements to https://github.com/Xembalo/hansol-aio-dashboard",
            usage="%(prog)s [options]")
    group = parser.add_argument_group('Reqired')         
    group.add_argument("--ess_host", help="Host or IP of your Samsung AIO ESS (e.g. \"192.168.1.25\")", required=True)

    group = parser.add_argument_group('MariaDB/MySQL')  
    group.add_argument("--mariadb_enabled",  default=False, help="Enable logging to mariadb/mysql", action="store_true")
    group.add_argument("--mariadb_host",     help="Host or IP of your database (e.g. localhost)", metavar='host/ip')
    group.add_argument("--mariadb_port",     type=int, default=3306, help="Port of your database (default: %(default)s)", metavar='port')
    group.add_argument("--mariadb_user",     help="Username", metavar='username')
    group.add_argument("--mariadb_pass",     help="Password", metavar='password')
    group.add_argument("--mariadb_database", help="Database in your mariadb/mysql instance", metavar='database')

    group = parser.add_argument_group('MQTT')  
    group.add_argument("--mqtt_enabled",           default=False, help="Enable publish stats to MQTT", action="store_true")
    group.add_argument("--mqtt_client_identifier", help="MQTT client identifier", metavar='identifier')
    group.add_argument("--mqtt_topic",             help="Topic for stats, like demand, feed-in or battery level", metavar='topic')
    group.add_argument("--mqtt_host",              help="Host or IP of your mqtt broker (e.g. localhost)", metavar='host/ip')
    group.add_argument("--mqtt_port",              type=int, default=1883, help="port of your mqtt broker (default: %(default)s)", metavar='port')
    group.add_argument("--mqtt_user",              help="Username for your mqtt broker", metavar='username')
    group.add_argument("--mqtt_pass",              help="Password for your mqtt broker", metavar='password')
    group.add_argument("--mqtt_qos",               type=int, choices=[0, 1], default=0, help="QoS of your messages [0/1]", metavar='qos-level')
    group.add_argument("--mqtt_force_config_broadcast", default=False, help="Force the MQTT sensor configuration to be transmitted at startup instead of only on the hour ", action="store_true")
    
    args = parser.parse_args()

    ESS_HOST                    = args.ess_host
    MARIADB_ENABLED             = args.mariadb_enabled
    MARIADB_HOST                = args.mariadb_host
    MARIADB_PORT                = args.mariadb_port
    MARIADB_USER                = args.mariadb_user
    MARIADB_PASS                = args.mariadb_pass
    MARIADB_DATABASE            = args.mariadb_database
    MQTT_ENABLED                = args.mqtt_enabled
    MQTT_CLIENT_IDENTIFIER      = args.mqtt_client_identifier
    MQTT_TOPIC                  = args.mqtt_topic
    MQTT_BROKER_ADDRESS         = args.mqtt_host
    MQTT_PORT                   = args.mqtt_port
    MQTT_USER                   = args.mqtt_user
    MQTT_PASS                   = args.mqtt_pass
    MQTT_QOS                    = args.mqtt_qos
    MQTT_FORCE_CONFIG_BROADCAST = args.mqtt_force_config_broadcast

    if not MARIADB_ENABLED and not MQTT_ENABLED:
        print('DB and MQTT disabled, nothing to do for me')
        sys.exit()

    #log the current time
    now = time.strftime("%Y-%m-%d %H:%M")

    #creates mqtt client if nessessary 
    if MQTT_ENABLED:
        client = mqtt.Client(MQTT_CLIENT_IDENTIFIER)
        if MQTT_USER != "":
            client.username_pw_set(username=MQTT_USER,password=MQTT_PASS)

        try:
            client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT) 
        except:
            print("MQTT connection failed")
            MQTT_ENABLED = False

    if not MARIADB_ENABLED and not MQTT_ENABLED:
        print('DB disabled and MQTT failed, nothing to do for me anymore')
        sys.exit()

    #create new session
    session = requests.Session()        

    #read device info, only at full hour and if MQTT is enabled
    if MQTT_ENABLED and (time.strftime("%M") == "00" or MQTT_FORCE_CONFIG_BROADCAST):
        model, sw_version, sn = readDeviceInfo(session)
        pushMqttConfig(client, model, sn, sw_version)
    
    #calc only if useful
    if MARIADB_ENABLED or MQTT_ENABLED: batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg, feedinbatteryavg, demandbatteryavg = calcStats(session)

    #insert into db
    if MARIADB_ENABLED: insertIntoMariadb(now, batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg)
    
    #push to mqtt and quits connection
    if MQTT_ENABLED: 
        pushMqttStats(client, now, batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg, feedinbatteryavg, demandbatteryavg)
        client.disconnect() # disconnect


if __name__ == "__main__":
   main()
