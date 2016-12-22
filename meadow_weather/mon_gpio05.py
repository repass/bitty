#!/usr/bin/python
#repass 10/10/15   monitor gpio5
import time
import RPi.GPIO as GPIO
import os
import logging
import sqlite3
import datetime

mon_pin = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(mon_pin,GPIO.IN)

logging.basicConfig(filename='/home/repass/log/weather.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.debug('Starting monitoring of gpio05')

con = sqlite3.connect('/home/repass/db/gpio.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

prev_input = 0
while True:
  #take a reading
  input = GPIO.input(mon_pin)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
#    logging.debug('switch gpio05 anemometer closed')
#    print("Switch gpio05 anemometer closed")

    now = datetime.datetime.now()
    with con:
         con.execute("insert into io(port, ts) values (?, ?)", (mon_pin, now))
    
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.05)

