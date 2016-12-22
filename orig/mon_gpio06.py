#!/usr/bin/python
#repass 10/10/15   monitor gpio6
import time
import RPi.GPIO as GPIO
import os
import logging

mon_pin = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(mon_pin,GPIO.IN)

logging.basicConfig(filename='gpio06.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.debug('Starting monitoring of gpio06')

prev_input = 0
while True:
  #take a reading
  input = GPIO.input(mon_pin)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
    logging.debug('switch closed')
    print("Switch gpio06 closed")
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.05)

