#!/usr/bin/bash

cd ~/Desktop/RPI_beobachtungsapp/src
source ../env/bin/activate

python cleanup.py

#flask run --host=0.0.0.0
python schaltung.py
