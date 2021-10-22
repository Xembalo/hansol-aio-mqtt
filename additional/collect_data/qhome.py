import requests
from bs4 import BeautifulSoup
import time
import pymysql

#Configuration
QHOME_URL = "http://192.168.1.25"
MARIADB_HOST = "localhost"
MARIADB_PORT = 3306
MARIADB_USER = "qhome"
MARIADB_PASS = "qhome"
MARIADB_DATABASE = "qhome"


#Read contents from qhome-stats-page
def readStats():

    #Read Table Cell next to a given cell by its content
    def findValue(caption):
        return float(soup.find(string=caption).parent.next_sibling.contents[0])

    session = requests.Session()
    response = session.get(QHOME_URL + ":21710/f0")
    soup = BeautifulSoup(response.text, features="html.parser")

    battery = findValue("BT_SOC")
    pv = findValue("PV_P(30s)")
    grid = findValue("GRID_P(30s)")
    temp = findValue("Temp")
    load = findValue("LOAD_P(30s)")

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

#log the current time
now = time.strftime("%Y-%m-%d %H:%M")

#Read values from stat page
battery1, pv1, demand1, feedin1, load1, temp1 = readStats()

#wait 31 seconds, qhome avg over 30 seconds
time.sleep(31)

#Read next stats
battery2, pv2, demand2, feedin2, load2, temp2 = readStats()

#calc avg values
batteryavg = (battery1 + battery2)/2
pvavg = (pv1 + pv2)/2000
demandavg = (demand1 + demand2)/2000
feedinavg = (feedin1 + feedin2)/2000
loadavg = (load1 + load2)/2000
tempavg = (temp1 + temp2)/2

#insert into db
insert_into_mariadb(now, batteryavg, pvavg, demandavg, feedinavg, loadavg, tempavg)