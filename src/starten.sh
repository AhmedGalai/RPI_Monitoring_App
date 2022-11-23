#!/usr/bin/bash

cd /home/pi/Desktop/RPI_Monitoring_App/src
source ../env/bin/activate

python cleanup.py

#flask run --host=0.0.0.0
python schaltung.py
