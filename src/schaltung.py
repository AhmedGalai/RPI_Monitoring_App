#!/usr/bin/python3


import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_DHT

## setup
DHT_SENSOR = Adafruit_DHT.DHT22

LICHT_PIN = 12
VENTIL_PIN = 31
DHT_PIN = 4
LUFT_BEFEUCHTER_PIN = 11

MAX_HUMIDITY = 90
MIN_HUMIDITY = 50

PAUSE_ZEIT = 60  #zeit zwischen messungen in sekunden

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LICHT_PIN, GPIO.OUT)
GPIO.setup(VENTIL_PIN, GPIO.OUT)
GPIO.setup(LUFT_BEFEUCHTER_PIN, GPIO.OUT)
GPIO_ausmachen(LICHT_PIN)
GPIO_ausmachen(VENTIL_PIN)
GPIO_anmachen(LUFT_BEFEUCHTER_PIN)
stop_error = False
licht_an = False
ventil_an = False
befeuchter_an = True

## functions

def update_txt_log(timestamp, humidity, temperature, light_on, moisterizer_on, ventil_on):
	line = f"\n| {timestamp} |       {'0' if humidity < 10}{humidity}%         |   {'0' if temperature < 10}{temperature}°C     |  {'an' if light_on else 'aus'}   |     {'an' if moisterizer_on else 'aus'}     |  {'an' if ventil_on else 'aus'}   |"
	with open("log.txt",'a') as file :
		file.write(line)

def GPIO_anmachen(pin):
	GPIO.output(pin, GPIO.HIGH)

def GPIO_ausmachen(pin):
	GPIO.output(pin, GPIO.LOW)

def DHT_lesen():
	h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	return h, t

def RPI_loop():
	breaking_error = False
	feuchtigkeit, temperatur = DHT_lesen()
	aktuelle_zeit = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	stunden = int(aktuelle_zeit[11:13])

	### licht

	if stunden in [13,18]: # stunden von 0 bis 23 für licht wählen
		GPIO_anmachen(LICHT_PIN)
		licht_an = True
	else :
		GPIO_ausmachen(LICHT_PIN)
		licht_an = False

	## ventil & befeuchter

	if feuchtigkeit > MAX_HUMIDITY :
		GPIO_anmachen(VENTIL_PIN)
		ventil_an = True
		GPIO_ausmachen(LUFT_BEFEUCHTER_PIN)
		befeuchter_an = False

	elif feuchtigkeit < MIN_HUMIDITY :
		GPIO_ausmachen(VENTIL_PIN)
		ventil_an = False
		GPIO_anmachen(LUFT_BEFEUCHTER_PIN)
		befeuchter_an = True

	#### ausgabe zu log.txt
	update_txt_log(aktuelle_zeit, feuchtigkeit, temperatur, licht_an, befeuchter_an, ventil_an)

	#breaking_error =     # notfall
	return breaking_error

while not stop_error :
	stop_error = RPI_loop()
	time.sleep(PAUSE_ZEIT)


# def main():
	# stop_error = False
	# while not stop_error :
	# 	stop_error = RPI_loop()

#GPIO.cleanup()

# if __name__ == '__main__':
# 	main()