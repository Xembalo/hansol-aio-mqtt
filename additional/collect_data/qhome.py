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
    
    response = session.get("http://" + ESS_HOST + ":21710/f0")
    soup = BeautifulSoup(response.text, features="html.parser")

    battery = float(findValue(soup, "BT_SOC"))
    pv = float(findValue(soup, "PV_P(30s)"))
    grid = float(findValue(soup, "GRID_P(30s)"))
    temp = float(findValue(soup, "Temp"))
    load = float(findValue(soup, "LOAD_P(30s)"))

    if grid >= 0:
        demand = grid
        feedin = 0
    else:
        demand = 0
        feedin = grid * -1

    return battery, pv, demand, feedin, load, temp

def calcStats(session):
    #Read values from stat page
    battery1, pv1, demand1, feedin1, load1, temp1 = readStats(session)

    #wait 31 seconds, qhome avg over 30 seconds
    time.sleep(31)

    #Read next stats
    battery2, pv2, demand2, feedin2, load2, temp2 = readStats(session)

    #calc avg values
    batteryavg = (battery1 + battery2)/2
    pvavg = (pv1 + pv2)/2000
    demandavg = (demand1 + demand2)/2000
    feedinavg = (feedin1 + feedin2)/2000
    loadavg = (load1 + load2)/2000
    tempavg = (temp1 + temp2)/2
    
    return batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg

def insertIntoMariadb(logdate, battery, pv, demand, feedin, load, temp):
    conn  = pymysql.connect(
                host=MARIADB_HOST, 
                user=MARIADB_USER, 
                password=MARIADB_PASS, 
                database=MARIADB_DATABASE,
                port = MARIADB_PORT
                )
    
    # Create a cursor object
    cur  = conn.cursor()

    query = f"INSERT INTO logs (date, demand, feedin, consumption, battery_percent, pv, temperature) VALUES ('{logdate}', '{demand}', '{feedin}', '{load}', '{battery}', '{pv}', '{temp}')"
    
    cur.execute(query)
    conn.commit()
    conn.close()

#push auto discovery info for home assistant
def pushMqttConfig(model_name, sn, sw_version):
    client = mqtt.Client(MQTT_CLIENT_IDENTIFIER)
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)

    
    data = {}
    data["name"] = "Batterie"
    data["unique_id"] = MQTT_TOPIC + "_battery"
    data["device"] = {}
    data["device"]["manufacturer"] = "Samsung"
    data["device"]["model"] = model_name
    data["device"]["name"] = "ESS 5.5 AiO"
    data["device"]["identifiers"] = [sn]
    data["device"]["sw_version"] = sw_version
    data["device_class"] = "battery"
    data["unit_of_measurement"] = "%"
    data["state_topic"] = MQTT_TOPIC + "/state"
    data["value_template"] = "{{ value_json.battery}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)
    
    data["name"] = "Photovoltaik"
    data["unique_id"] = MQTT_TOPIC + "_pv"
    data["device_class"] = "power"
    data["state_class"] = "measurement"
    data["unit_of_measurement"] = "kW"
    data["icon"] = "mdi:solar-power"
    data["value_template"] = "{{ value_json.pv}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)

    data["name"] = "Entnahme vom Netz"
    data["unique_id"] = MQTT_TOPIC + "_demand"
    del data['icon']
    data["value_template"] = "{{ value_json.demand}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)

    data["name"] = "Einspeisung"
    data["unique_id"] = MQTT_TOPIC + "_feedin"
    data["value_template"] = "{{ value_json.feedin}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)

    data["name"] = "Last"
    data["unique_id"] = MQTT_TOPIC + "_load"
    data["value_template"] = "{{ value_json.load}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)

    data["name"] = "Temperatur"
    data["unique_id"] = MQTT_TOPIC + "_temperature"
    data["device_class"] = "temperature"
    data["unit_of_measurement"] = "°C"
    data["state_topic"] = MQTT_TOPIC + "/state"
    data["value_template"] = "{{ value_json.temp}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)
    
    client.loop()

def pushMqttStats(logdate, battery, pv, demand, feedin, load, temp):
    client = mqtt.Client(MQTT_CLIENT_IDENTIFIER)
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)
    
    data = {}
    data["date"] = logdate
    data["battery"] = battery
    data["pv"] = pv
    data["demand"] = demand
    data["feedin"] = feedin
    data["load"] = load
    data["temp"] = temp
    
    client.publish(MQTT_TOPIC + "/state", json.dumps(data), qos=MQTT_QOS)

    client.loop()

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
    MQTT_QOS                    = args.mqtt_qos
    MQTT_FORCE_CONFIG_BROADCAST = args.mqtt_force_config_broadcast

    if not MARIADB_ENABLED and not MQTT_ENABLED:
        print('DB and MQTT disabled, nothing to do for me')
        sys.exit()

    #log the current time
    now = time.strftime("%Y-%m-%d %H:%M")

    #create new session
    session = requests.Session()

    #Read device info, only at full hour and if MQTT is enabled
    if MQTT_ENABLED and (time.strftime("%M") == "00" or MQTT_FORCE_CONFIG_BROADCAST):
        model, sw_version, sn = readDeviceInfo(session)
        pushMqttConfig(model, sn, sw_version)
    
    #calc only if useful
    if MARIADB_ENABLED or MQTT_ENABLED: batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg = calcStats(session)

    #insert into db
    if MARIADB_ENABLED: insertIntoMariadb(now, batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg)
    
    #push to mqtt
    if MQTT_ENABLED: pushMqttStats(now, batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg)

if __name__ == "__main__":
   main()
