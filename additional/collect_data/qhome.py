from typing import TYPE_CHECKING
import requests
from bs4 import BeautifulSoup
import time
import pymysql
import paho.mqtt.client as mqtt
import json

#Configuration
QHOME_URL = "http://192.168.1.25"
MARIADB_HOST = "localhost"
MARIADB_PORT = 3307
MARIADB_USER = "qhome"
MARIADB_PASS = "qhome"
MARIADB_DATABASE = "qhome"
MQTT_CLIENT_IDENTIFIER = "qhome"
MQTT_TOPIC = "qhome"
MQTT_BROKER_ADDRESS = "localhost"
MQTT_PORT = 1883
MQTT_QOS = 1

#Read Table Cell next to a given cell by its content
def findValue(soup, caption):
    return soup.find(string=caption).parent.next_sibling.contents[0].strip()

#Read general information
def readDeviceInfo(session):
    response = session.get(QHOME_URL + ":21710/f0")
    soup = BeautifulSoup(response.text, features="html.parser")

    model = findValue(soup, "EMS-Model Name")
    sw_version = findValue(soup, "EMS Version")

    response = session.get(QHOME_URL + ":21710/f8")
    soup = BeautifulSoup(response.text, features="html.parser")

    sn = findValue(soup, "S-Number")

    return model, sw_version, sn

#Read contents from qhome-stats-page
def readStats(session):
    
    response = session.get(QHOME_URL + ":21710/f0")
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

def insert_into_mariadb(logdate, battery, pv, demand, feedin, load, temp):
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

def push_mqtt(logdate, battery, pv, demand, feedin, load, temp, model_name, sn, sw_version):
    client = mqtt.Client(MQTT_CLIENT_IDENTIFIER)
    client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)

    #push auto discovery info for home assistant
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
    #data["icon"] = "hass:battery"
    data["unit_of_measurement"] = "%"
    data["state_topic"] = MQTT_TOPIC + "/state"
    data["value_template"] = "{{ value_json.battery}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)
    
    data["name"] = "Photovoltaik"
    data["unique_id"] = MQTT_TOPIC + "_pv"
    data["device_class"] = "energy"
    #data["icon"] = "hass:bolt"
    data["unit_of_measurement"] = "kWh"
    data["value_template"] = "{{ value_json.pv}}"
    client.publish("homeassistant/sensor/" + data["unique_id"] + "/config", json.dumps(data), qos=MQTT_QOS)

    data["name"] = "Entnahme vom Netz"
    data["unique_id"] = MQTT_TOPIC + "_demand"
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

#create new session
session = requests.Session()

#log the current time
now = time.strftime("%Y-%m-%d %H:%M")

#Read device info
model, sw_version, sn = readDeviceInfo(session)

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

#insert into db
insert_into_mariadb(now, batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg)

push_mqtt(now, batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg, model, sn, sw_version)