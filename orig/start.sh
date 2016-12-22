#!/bin/sh
echo "Starting Weather Monitoring Scripts\n";
./mon_gpio05.py&
./mon_gpio13.py&
