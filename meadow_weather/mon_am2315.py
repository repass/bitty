#!/usr/bin/python
import time
import os
import logging
import sqlite3
import datetime

from tentacle_pi.AM2315 import AM2315
am = AM2315(0x5c,"/dev/i2c-1")

logging.basicConfig(filename='/home/repass/log/weather.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.debug('Starting monitoring of am2315 outdoor temperature/humidity')

con = sqlite3.connect('/home/repass/db/am2315.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

while True:
        temperature, humidity, crc_check = am.sense()
        now = datetime.datetime.now()
        with con:
             con.execute("insert into am2315(ts, temperature, humidity) values (?, ?, ?)", (now, temperature, humidity))

#        mytemp="temperature: %s %s humidity: %s" % ((temperature * 1.8 + 32),temperature,humidity )
        logging.debug("outdoor temperature: %sC %sF humidity: %s" % (temperature,(temperature * 1.8 + 32),humidity)) 
#        logging.debug "temperature: %s %s" % ((temperature * 1.8 + 32),temperature ) 
#        print "temperature: %s %s" % ((temperature * 1.8 + 32),temperature )
#        print "humidity: %s" % humidity
#        logging.debug "humidity: %s" % humidity
#        print "crc: %s" % crc_check
        time.sleep(60)


