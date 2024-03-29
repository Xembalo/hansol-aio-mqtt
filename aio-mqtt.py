#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time
import pymysql
import paho.mqtt.client as mqtt
import json
import sys
import argparse
import signal
import logging
import os
import csv
 
from mqtt_homeassistant_utils import HADevice, HASensor, HABinarySensor, HASensorEnergy, HASensorBattery, HASensorTemperature, HADeviceClassBinarySensor
from errorcodes import errorcodes

#global Variables
loopEnabled = True
ESS_HOST = ""
MARIADB_ENABLED = False
MARIADB_HOST = ""
MARIADB_PORT = 0
MARIADB_USER = ""
MARIADB_PASS = ""
MARIADB_DATABASE = ""
MQTT_ENABLED = False
MQTT_CLIENT_IDENTIFIER = ""
MQTT_TOPIC = ""
MQTT_BROKER_ADDRESS = ""
MQTT_PORT = 0
MQTT_QOS = 0
MQTT_USER = ""
MQTT_PASS = ""
HADEVICE = None


#Name of temporary file storage
MISSING_INSERTS_FILE_NAME = "missing_inserts.txt"

#Read Table Cell next to a given cell by its content
def findValue(soup, caption):
    return soup.find(string=caption).parent.next_sibling.contents[0].strip()

def findErrors(soup):
    return soup.find(string=" Error Code String ").parent.parent.next_sibling.next_sibling.contents[0].contents[0].strip().lstrip("|").rstrip("$")

#Read general information
def readDeviceInfo(session):
    global HADEVICE

    for attempt in range(10):
        try:
            logging.info("Fetching device info attempt %s", str(attempt))
            response = session.get("http://" + ESS_HOST + ":21710/f0")
        except:
            time.sleep(10)
        else:
            break
    else:
        raise ValueError('myess not reachable')

    soup = BeautifulSoup(response.text, features="html.parser")

    model = findValue(soup, "EMS-Model Name")
    version = findValue(soup, "EMS Version")

    response = session.get("http://" + ESS_HOST + ":21710/f8")
    soup = BeautifulSoup(response.text, features="html.parser")

    sn = findValue(soup, "S-Number")

    HADEVICE = HADevice(
        manufacturer="Samsung", 
        model=model,
        name="ESS 5.5 AiO",
        sw_version=version,
        identifiers=[sn],
        configuration_url="http://" + ESS_HOST + ":21710"
    )


#Read contents from qhome-stats-page
def readStats(session, with_errors):
    for attempt in range(10):
        try:
            logging.info("Fetching statts attempt %s", str(attempt))
            response = session.get("http://" + ESS_HOST + ":21710/f8")
        except:
            time.sleep(10)
        else:
            break
    else:
        raise ValueError('myess not reachable')
    
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

    #Evaluate Errors only once
    if with_errors:
        errcode = findErrors(soup)
        if errcode != "":
            if errcode in errorcodes:
                err = errorcodes[errcode]
                err["code"] = errcode
                err["state"] = "ON"
            else:
                err = {"category":"WARNUNG","title":"UNBEKANNTER FEHLER","action":"Unbekannter Fehler","code":errcode,"state":"ON"}
        else:
            err = {"state":"OFF"}
        
        return battery, pv1, pv2, demand, feedin, load, temp, err
    else:
        return battery, pv1, pv2, demand, feedin, load, temp  

def calcStats(session):
    #Read values from stat page
    battery1, pv11, pv21, demand1, feedin1, consumption1, temp1, err = readStats(session, True)

    #wait 30 seconds, qhome avg over 30 seconds
    time.sleep(30)

    #Read next stats
    battery2, pv12, pv22, demand2, feedin2, consumption2, temp2 = readStats(session, False)

    #calc avg values
    batteryavg = (battery1 + battery2)/2
    tempavg = (temp1 + temp2)/2
    pv1avg = ((pv11 + pv12)/2000)/60 #divide by 60, 'cause we fetch every minute,
    pv2avg = ((pv21 + pv22)/2000)/60 
    demandgridavg = ((demand1 + demand2)/2000)/60
    feedingridavg = ((feedin1 + feedin2)/2000)/60
    consumptionavg = ((consumption1 + consumption2)/2000)/60
    
    #calc battery feedin or demand
    if pv1avg + pv2avg + demandgridavg > feedingridavg + consumptionavg:
        demandbatteryavg = 0
        feedinbatteryavg = pv1avg + pv2avg + demandgridavg - feedingridavg - consumptionavg
    else:
        feedinbatteryavg = 0
        demandbatteryavg = consumptionavg + feedingridavg - pv1avg - pv2avg - demandgridavg
    
    return batteryavg, pv1avg, pv2avg, demandgridavg, feedingridavg, consumptionavg, tempavg, feedinbatteryavg, demandbatteryavg, err

def generateInsert(values):
    return f"INSERT INTO logs (date, demand, feedin, consumption, battery_percent, pv, pv1, pv2, temperature) VALUES (str_to_date('{values[0]}', '%Y-%m-%d %H:%i:%s'), {values[1]}, {values[2]}, {values[3]}, {values[4]}, {values[5]}, {values[6]}, {values[7]}, {values[8]})"

def importMissingInsertsIntoMariadb(conn):
    success = True

    if os.path.exists(MISSING_INSERTS_FILE_NAME):
        with open(MISSING_INSERTS_FILE_NAME) as f:
            reader = csv.reader(f)
            for line in reader:
                try:
                    cur = conn.cursor()
                    query = generateInsert(tuple(line))
                    cur.execute(query)
                except:
                    success = False
            
            if success:
                conn.commit()
        
        if success:
            os.remove(MISSING_INSERTS_FILE_NAME)

def logMissingInsertToFile(csv_values):
    with open(MISSING_INSERTS_FILE_NAME, 'a') as f:
        file_writer = csv.writer(f, lineterminator='\n')
        file_writer.writerow(csv_values)

def insertIntoMariadb(logdate, battery, pv1, pv2, demand, feedin, consumption, temp):
    pv = pv1 + pv2
    csv_values = (logdate, demand, feedin, consumption, battery, pv, pv1, pv2, temp)
    query = generateInsert(csv_values)

    success = False
    try:
        conn  = pymysql.connect(
                    host=MARIADB_HOST, 
                    user=MARIADB_USER, 
                    password=MARIADB_PASS, 
                    database=MARIADB_DATABASE,
                    port = MARIADB_PORT
                    )
        cur  = conn.cursor()
        
        cur.execute(query)
        conn.commit()

        success = True
    except pymysql.Error as err:
        logMissingInsertToFile(csv_values)
        success = False
    
    if success:
        importMissingInsertsIntoMariadb(conn)
    try:
        conn.close()
    except:
        pass

#push auto discovery info for home assistant
def pushMqttConfig(mqttclient: mqtt.Client, device: HADevice):
    logging.info("pushing online message and auto discovery info for home assistant")
    
    #Status/Alive Message
    mqttclient.publish(MQTT_TOPIC + "/state", "online", qos=MQTT_QOS, retain=True)

    sensor = HASensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_state",
        name="Status",
        state_topic=MQTT_TOPIC + "/state",
        device=device        
    )
    sensor.publish(mqttclient,MQTT_QOS)
    
    #Sensor config
    sensor = HASensorBattery(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_battery",
        name="Batterie",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.battery }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)
    
    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_pv1",
        name="Photovoltaik 1",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        icon="mdi:solar-power",
        value_template="{{ value_json.pv1 }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)
    
    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_pv2",
        name="Photovoltaik 2",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        icon="mdi:solar-power",
        value_template="{{ value_json.pv2 }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_demand_grid",
        name="Entnahme vom Netz",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.demandgrid }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_feedin_grid",
        name="Einspeisung ins Netz",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.feedingrid }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_consumption",
        name="Hausverbrauch",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.consumption }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_demand_battery",
        name="Entnahme aus Batterie",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.demandbattery }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorEnergy(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_feedin_battery",
        name="Einspeisung in Batterie",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.feedinbattery }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensorTemperature(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_temperature",
        name="Temperatur",
        state_topic=MQTT_TOPIC + "/values",
        device=device,
        value_template="{{ value_json.temperature }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)
    
    #Errorstate
    sensor = HABinarySensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_error",
        name="Fehler",
        state_topic=MQTT_TOPIC + "/errors",
        device=device,
        device_class=HADeviceClassBinarySensor.PROBLEM,
        value_template="{{ value_json.state }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_errorcode",
        name="Fehlercode",
        state_topic=MQTT_TOPIC + "/errors",
        device=device,
        value_template="{{ value_json.code }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_errorcategory",
        name="Fehlerkategorie",
        state_topic=MQTT_TOPIC + "/errors",
        device=device,
        value_template="{{ value_json.category }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_errortitle",
        name="Fehlertitel",
        state_topic=MQTT_TOPIC + "/errors",
        device=device,
        value_template="{{ value_json.title }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

    sensor = HASensor(
        node_id=MQTT_TOPIC,
        unique_id=MQTT_TOPIC + "_erroraction",
        name="Fehleraktion",
        state_topic=MQTT_TOPIC + "/errors",
        device=device,
        value_template="{{ value_json.action }}"
    )
    sensor.publish(mqttclient,MQTT_QOS)

def pushMqttStats(mqttclient, logdate, battery, pv1, pv2, demandgrid, feedingrid, consumption, temp, feedinbattery, demandbattery, err):  
    data = {}
    data["date"] = logdate
    data["battery"] = battery
    data["pv"] = round(pv1 + pv2, 5)
    data["pv1"] = round(pv1, 5)
    data["pv2"] = round(pv2, 5)
    data["demandgrid"] = round(demandgrid, 5)
    data["feedingrid"] = round(feedingrid, 5)
    data["consumption"] = round(consumption, 5)
    data["feedinbattery"] = round(feedinbattery, 5)
    data["demandbattery"] = round(demandbattery, 5)
    data["temperature"] = round(temp, 1)
    
    mqttclient.publish(MQTT_TOPIC + "/values", json.dumps(data), qos=MQTT_QOS)
    mqttclient.publish(MQTT_TOPIC + "/errors", json.dumps(err), qos=MQTT_QOS)

def mqttOnConnect(client, userdata, flags, rc):
    if rc==0:
        logging.info('MQTT connected')
        client.connected_flag = True
        pushMqttConfig(client, HADEVICE)
    else:
        logging.info("Bad connection Returned code=",rc)
    
def mqttOnDisconnect(client, userdata, rc):
    logging.info("MQTT disconnected")
    client.connected_flag = False

def signalHandler(signal, frame):
    global loopEnabled
    print("Got quit signal, cleaning up...")
    loopEnabled = False

def parseArguments():
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

    parser = argparse.ArgumentParser(
            description="Reads stats from Samsung/Hansol AIO ESS 5.5 web inteface and push to Database and/or MQTT", 
            epilog="Report bugs, comments or improvements to https://github.com/Xembalo/hansol-aio-dashboard",
            usage="%(prog)s [options]")
    group = parser.add_argument_group('Reqired')         
    group.add_argument("--ess_host", help="Host or IP of your Samsung/Hansol AIO ESS (e.g. \"192.168.1.25\")", required=True)

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


def main():
    logging.basicConfig(filename='qhome_endless.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Script started')

    parseArguments()
    if not MARIADB_ENABLED and not MQTT_ENABLED:
        print('DB and MQTT disabled, nothing to do for me')
        sys.exit()

    #create new session
    session = requests.Session()

    #Signal Handler for interrupting the loop
    signal.signal(signal.SIGINT, signalHandler)

    if MQTT_ENABLED:
        mqtt.Client.connected_flag = False

        client = mqtt.Client(MQTT_CLIENT_IDENTIFIER)
        client.on_connect = mqttOnConnect
        client.on_disconnect = mqttOnDisconnect

        if MQTT_USER != "":
            client.username_pw_set(username=MQTT_USER,password=MQTT_PASS)

        client.will_set(MQTT_TOPIC + "/state","offline",MQTT_QOS,retain=True)

        #read device info, only if MQTT is enabled
        readDeviceInfo(session)

        try:
            logging.info("try to connect")
            client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)
            logging.info("starting the MQTT background loop")  
            client.loop_start()
        except:
            #if connection was not successful, try it in next loop again
            logging.info("connection was not successful, try it in next loop again")
    
    while loopEnabled:
        logging.info("main loop")

        #log the current time
        now = time.strftime("%Y-%m-%d %H:%M")
        
        #calc only if useful
        if MARIADB_ENABLED or MQTT_ENABLED: 
            batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg, feedinbatteryavg, demandbatteryavg, err = calcStats(session)

        #insert into db
        if MARIADB_ENABLED: 
            insertIntoMariadb(now, batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg)

        #push to mqtt and quits connection
        if MQTT_ENABLED and client.connected_flag: 
            pushMqttStats(client, now, batteryavg, pv1avg, pv2avg, demandavg, feedingridavg, consumptiongridavg, tempavg, feedinbatteryavg, demandbatteryavg, err)
        
        #wait another 30 seconds
        time.sleep(30.0 - time.time() % 30.0)

    #send last message
    client.publish(MQTT_TOPIC + "/state", "offline", qos=MQTT_QOS, retain=True)
    client.loop_stop()  
    client.disconnect() 

if __name__ == "__main__":
   main()

