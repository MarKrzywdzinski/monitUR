#!/bin/bash
sleep 10
python3 /home/pi/raspberry/PICmeBot_AmperWorks_SensorBoard.py &
sleep 10
python3 /home/pi/raspberry/app.py 
