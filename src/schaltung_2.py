#!/usr/bin/python3


import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_DHT
import requests
import ast

## setup
DHT_SENSOR = Adafruit_DHT.DHT11

LICHT_PIN = 27
VENTIL_PIN = 22
DHT_PIN = 4
LUFT_BEFEUCHTER_PIN = 26

LICHT_ARBEIT_STUNDEN = [13, 18] # stunden von 0 bis 23 für licht wählen
MAX_HUMIDITY = 70
MIN_HUMIDITY = 60

PAUSE_ZEIT = 10  #zeit zwischen messungen in sekunden

GPIO.setmode(GPIO.BCM)
GPIO.setup(LICHT_PIN, GPIO.OUT)
GPIO.setup(VENTIL_PIN, GPIO.OUT)
GPIO.setup(LUFT_BEFEUCHTER_PIN, GPIO.OUT)

stop_error = False
licht_an = False
ventil_an = False
befeuchter_an = True

licht_kontroll_auto = True
ventil_kontroll_auto = True
befeuchter_kontroll_auto = True
licht_kontroll_an = True
ventil_kontroll_an = True
befeuchter_kontroll_an = True

## functions

def update_txt_log(timestamp, humidity, temperature, light_on, moisterizer_on, ventil_on):
	line = f"\n| {timestamp} |       {'0' if humidity < 10 else ''}{humidity}%       |   {'0' if temperature < 10 else ''}{temperature}°C   |  {' an' if light_on else 'aus'}  |    {' an' if moisterizer_on else 'aus'}     |  {' an' if ventil_on else 'aus'}   |"
	with open("log2.txt",'a') as file :
		file.write(line)

def GPIO_anmachen(pin):
	GPIO.output(pin, GPIO.HIGH)

def GPIO_ausmachen(pin):
	GPIO.output(pin, GPIO.LOW)

def licht_anmachen():
	GPIO_anmachen(LICHT_PIN)
	licht_an = True

def licht_ausmachen():
	GPIO_ausmachen(LICHT_PIN)
	licht_an = False

def ventil_anmachen():
	GPIO_anmachen(VENTIL_PIN)
	ventil_an = True

def ventil_ausmachen():
	GPIO_ausmachen(VENTIL_PIN)
	ventil_an = False

def befeuchter_anmachen():
	GPIO_anmachen(LUFT_BEFEUCHTER_PIN)
	befeuchter_an = True

def befeuchter_ausmachen():
	GPIO_ausmachen(LUFT_BEFEUCHTER_PIN)
	befeuchter_an = False


def DHT_lesen():
	h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	return h, t

def auto_licht():
	if stunden in LICHT_ARBEIT_STUNDEN:
		licht_anmachen()
	else :
		licht_ausmachen()

def auto_humidity(feuchtigkeit, ventil_auto, befeuchter_auto):
	if feuchtigkeit > MAX_HUMIDITY :
		if ventil_auto :
			ventil_anmachen()
		if befeuchter_auto :
			befeuchter_ausmachen()

	elif feuchtigkeit < MIN_HUMIDITY :
		if ventil_auto :
			ventil_ausmachen()
		if befeuchter_auto :
			befeuchter_anmachen()


def RPI_loop(licht_kontroll_an,licht_kontroll_auto,ventil_kontroll_an,ventil_kontroll_auto,befeuchter_kontroll_an,befeuchter_kontroll_auto):

	licht_an = False
	ventil_an = False
	befeuchter_an = True
	breaking_error = False
	feuchtigkeit, temperatur = DHT_lesen()
	aktuelle_zeit = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	stunden = int(aktuelle_zeit[11:13])

	### licht
	if licht_kontoll_auto :
		auto_licht()
	elif licht_kontroll_an :
		licht_anmachen()
	else :
		licht_ausmachen()


	## ventil & befeuchter
	auto_humidity(feuchtigkeit, ventil_kontroll_auto, befeuchter_kontroll_auto)
	if not ventil_kontroll_auto :
		if ventil_kontroll_an :
			ventil_anmachen()
		else :
			ventil_ausmachen()

	if not befeuchter_kontroll_auto :
		if befeuchter_kontroll_an :
			befeuchter_anmachen()
		else :
			befeuchter_ausmachen()

	
	#### ausgabe zu log.txt
	update_txt_log(aktuelle_zeit, feuchtigkeit, temperatur, licht_an, befeuchter_an, ventil_an)
	
	#breaking_error =     # notfall
	return breaking_error

def main():
	stop_error = False
	GPIO_ausmachen(LICHT_PIN)
	GPIO_ausmachen(VENTIL_PIN)
	GPIO_anmachen(LUFT_BEFEUCHTER_PIN)
	while not stop_error :
		r = ast.literal_eval(requests.get('http://0.0.0.0:5000').text)
		licht_kontroll_an = r['licht_an']
		licht_kontroll_auto = r['licht_auto']
		ventil_kontroll_an = r['ventil_an']
		ventil_kontroll_auto = r['ventil_auto']
		befeuchter_kontroll_an = r['befeuchter_an']
		befeuchter_kontroll_auto = r['befeuchter_auto']
		kontroll_daten = [licht_kontroll_an,licht_kontroll_auto,ventil_kontroll_an,ventil_kontroll_auto,befeuchter_kontroll_an,befeuchter_kontroll_auto]
		stop_error = RPI_loop(kontroll_daten)
		time.sleep(PAUSE_ZEIT)

	GPIO.cleanup()

############ Program starter hier ##############################
if __name__ == '__main__':
	main()
