#!/bin/sh
echo "Starting Weather Monitoring Scripts\n";
/home/repass/src/meadow_weather/mon_gpio05.py&
/home/repass/src/meadow_weather/mon_gpio13.py&
/home/repass/src/meadow_weather/mon_am1235.py&
/home/repass/src/Adafruit_Python_BMP/examples/mon_bmp180.py&
/home/repass/src/ads1115/mon_ads1115.py&
