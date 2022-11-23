
#!/env/bin/python3

import RPi.GPIO as GPIO
import time
import datetime
import Adafruit_DHT
import requests
import ast
import json
from rich import print
import subprocess
from flask import g
from app import app, init_db, update_db
import sqlite3

DATABASE = '/home/pi/Desktop/RPI_Monitoring_App/src/sql.db'
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

URL = 'http://0.0.0.0:5000'


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

def get_data():
	r = ast.literal_eval(requests.get(f"{URL}/kontroll").text)
	licht_kontroll_an = r['licht_an']
	licht_kontroll_auto = r['licht_auto']
	ventil_kontroll_an = r['ventil_an']
	ventil_kontroll_auto = r['ventil_auto']
	befeuchter_kontroll_an = r['befeuchter_an']
	befeuchter_kontroll_auto = r['befeuchter_auto']
	return licht_kontroll_an,licht_kontroll_auto,ventil_kontroll_an,ventil_kontroll_auto,befeuchter_kontroll_an,befeuchter_kontroll_auto

def post_data(timestamp, humidity, temperature):

	client = requests.session()

	# Retrieve the CSRF token first
	client.get(URL)  # sets cookie
	if 'csrftoken' in client.cookies:
	    # Django 1.6 and up
	    csrftoken = client.cookies['csrftoken']
	elif 'csrf' in client.cookies:
	    # older versions
	    csrftoken = client.cookies['csrf']
	else :
	    csrftoken = ''

	data = dict(timestamp=timestamp, humidity=humidity, temperature=temperature, csrfmiddlewaretoken=csrftoken)
	r = client.post(f"{URL}", json=data, headers=dict(Referer=URL))
	return r


def DHT_lesen():
	h, t = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	return h, t

def auto_licht(stunden):
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
	licht_an = True
	ventil_an = True
	befeuchter_an = True
	feuchtigkeit, temperatur = DHT_lesen()
	aktuelle_zeit = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
	stunden = int(aktuelle_zeit[11:13])

	### licht
	if licht_kontroll_auto :
		auto_licht(stunden)
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
	#update_txt_log(aktuelle_zeit, feuchtigkeit, temperatur, licht_an, befeuchter_an, ventil_an)
	
	try:
		res = post_data(aktuelle_zeit, feuchtigkeit, temperatur)
		posted_data = res.json()
	except Exception as e:
		print("error while posting data to webApp: ")
		print(f"[red]{e}[/red]")
		posted_data = None
	
	print("posted data to webapp: ")
	print(posted_data)
	breaking_error = False
	#breaking_error =     # notfall
	with app.app_context():
		update_db(temperatur, feuchtigkeit, aktuelle_zeit)
	return breaking_error

def main():
	with app.app_context():
		init_db()
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
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

	while not stop_error :
		try:
			kontroll_daten = get_data()
		except Exception as e:
			print("error while getting control data: ")
			print(f"[red]{e}[/red]")
			kontroll_daten = (True, True, True, True, True, True)
		print("erworbene kontroll daten: ")
		print(kontroll_daten)
		stop_error = RPI_loop(*kontroll_daten)
		time.sleep(PAUSE_ZEIT)


############ Program starter hier ##############################
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass

	GPIO.cleanup()
	subprocess.run(['rm','sql.db'])
