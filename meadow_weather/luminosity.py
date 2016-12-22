#!/usr/bin/python
#repass 10/10/15 read i2c humidity value from hex 40 bus 1

import smbus
import time

bus = smbus.SMBus(1)

DEVICE_ADDRESS = 0x39

#power up lum device
Command = 0x03
bus.write_byte_data(DEVICE_ADDRESS,Command)

def humidity():
	humid=bus.read_byte_data(DEVICE_ADDRESS,0x00)
	return humid

while True:
	h=humidity()
	print h
	time.sleep(1)
