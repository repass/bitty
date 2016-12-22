#!/usr/bin/env python3
#modified repass 10/13/15 to record to sqlite3
import time
import quick2wire.i2c as i2c
import binascii

import sqlite3
import datetime
import logging
import os


class CRCFailed(Exception): pass

class HTU21D:

    CMD_READ_TEMP_HOLD = 0xe3
    CMD_READ_HUM_HOLD = 0xe5
    CMD_READ_TEMP_NOHOLD = 0xf3
    CMD_READ_HUM_NOHOLD = 0xf5
    CMD_WRITE_USER_REG = 0xe6
    CMD_READ_USER_REG = 0xe7
    CMD_SOFT_RESET= 0xfe

    # all HTU21Ds are hardcoded to this address.
    ADDR = 0x40

    # uses bits 7 and 0 of the user_register mapping
    # to the bit resolutions of (relative humidity, temperature)
    RESOLUTIONS = {
        (0, 0) : (12, 14),
        (0, 1) : (8, 12),
        (1, 0) : (10, 13),
        (1, 1) : (11, 11),
    }

    # sets up the times to wait for measurements to be completed. uses the
    # max times from the datasheet plus a healthy safety margin (10-20%)
    MEASURE_TIMES = {
        (12, 14): (.018, .055),
        (8, 12): (.005, .015),
        (10, 13): (.006, .028),
        (11, 11): (.01, .009),
    }

    def __init__(self, debug=False):
        self.bus = i2c.I2CMaster()
        self.resolutions = self.get_resolutions()
        self.rh_timing, self.temp_timing = self.MEASURE_TIMES[self.resolutions]
        self.debug = debug
        
    def check_crc(self, sensor_val):
        """
        Adapted from https://github.com/sparkfun/HTU21D_Breakout/blob/master/Library/HTU21D_Humidity/HTU21D.cpp
        
        Give this function the 3 byte reading from the HTU21D
        If it returns 0, then the transmission was good
        If it returns something other than 0, then the communication was corrupted
        From: http://www.nongnu.org/avr-libc/user-manual/group__util__crc.html
        POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1 : http://en.wikipedia.org/wiki/Computation_of_cyclic_redundancy_checks

        Test cases from datasheet:
            message = 0xDC, checkvalue is 0x79
            message = 0x683A, checkvalue is 0x7C
            message = 0x4E85, checkvalue is 0x6B
        """
        message_from_sensor = sensor_val >> 8
        check_value_from_sensor = sensor_val & 0x0000FF

        remainder = message_from_sensor << 8 # Pad with 8 bits because we have to add in the check value
        remainder |= check_value_from_sensor # Add on the check value

        divisor = 0x988000 # This is the 0x0131 polynomial shifted to farthest left of three bytes

        # Operate on only 16 positions of max 24. The remaining 8 are our remainder and should be zero when we're done.
        for i in range(16):
            if self.debug:
                print("remainder: {0:024b}".format(remainder));
                print("divisor:   {0:024b}".format(divisor));

            if remainder & (1<<(23 - i)):  #Check if there is a one in the left position
              remainder ^= divisor

            divisor >>= 1 # Rotate the divisor max 16 times so that we have 8 bits left of a remainder

        if remainder:
            raise CRCFailed("CRC checksum failed.")

    def reset(self):
        self.bus.transaction(i2c.writing_bytes(self.ADDR, self.CMD_SOFT_RESET))
        time.sleep(.02)

    def get_resolutions(self):
        user_reg = self.bus.transaction(
            i2c.writing_bytes(self.ADDR, self.CMD_READ_USER_REG),
            i2c.reading(self.ADDR, 1),
        )
        user_reg_int = int.from_bytes(user_reg[0], byteorder="big")
        return self.RESOLUTIONS[user_reg_int >> 6, user_reg_int & 0x1]
        
    def get_temp(self):
        self.bus.transaction(i2c.writing_bytes(self.ADDR, self.CMD_READ_TEMP_NOHOLD))
        time.sleep(self.temp_timing)
        results = self.bus.transaction(i2c.reading(self.ADDR, 3))

        raw_reading = results[0]
        if self.debug:
            print(binascii.hexlify(raw_reading))

        raw_temp = int.from_bytes(raw_reading, byteorder="big")
        self.check_crc(raw_temp)
        return -46.85 + (175.72 * ((raw_temp >> 8) / float(2**16)))

    def get_rel_humidity(self):
        self.bus.transaction(i2c.writing_bytes(self.ADDR, self.CMD_READ_HUM_NOHOLD))
        time.sleep(self.rh_timing)
        results = self.bus.transaction(i2c.reading(self.ADDR, 3))

        raw_reading = results[0]
        if self.debug:
            print(binascii.hexlify(raw_reading))

        raw_hum = int.from_bytes(raw_reading, byteorder="big")
        self.check_crc(raw_hum)
        return -6 + (125 * ((raw_hum >> 8) / float(2**16)))


logging.basicConfig(filename='/home/repass/log/weather.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.debug('Starting monitoring of htu21d')

con = sqlite3.connect('/home/repass/db/weather.db',detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


if __name__ == '__main__':
    sensor = HTU21D()
    while True:
        now = datetime.datetime.now()
        sensor.reset()
        #print(now, sensor.get_temp(), sensor.get_rel_humidity())
        #logging.debug(now, sensor.get_temp(), sensor.get_rel_humidity())
        with con:
            con.execute("insert into htu21d(temperature, humidity, ts) values (?, ?, ?)", (sensor.get_temp(), sensor.get_rel_humidity(), now))
        time.sleep(60.0)
