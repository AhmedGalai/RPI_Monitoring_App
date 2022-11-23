#!/env/bin/python3

from flask import g, Flask, redirect, url_for, render_template, Markup, request, jsonify
import json
import sqlite3
from rich import print
#import threading
#import subprocess

DATABASE = '/home/pi/Desktop/RPI_Monitoring_App/src/sql.db'
app = Flask(__name__)

# event = threading.event


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET': #### get most recent values from db
		zyklus = query_db('select * from Zyklus where current = 1', [], one=True)
		temperatur = zyklus.temperatur
		feuchtigkeit = zyklus.feuchtigkeit
		temperatur = 'nicht verbunden'
		feuchtigkeit = 'nicht verbunden'
		#with open('log.txt','r') as log :
			#temperatur = log[:]
			#feuchtigkeit = log[:]
		return render_template("index.html",TEMPERATUR=temperatur,FEUCHTIGKEIT=feuchtigkeit)
	if request.method == 'POST': #### update the values
		data = request.json
		timestamp = data['timestamp']
		temperatur = data['temperature']
		feuchtigkeit = data['humidity']
		query_db('Update Zyklus set temperatur = ? where current = 1', [temperatur], one=True)
		query_db('Update Zyklus set feuchtigkeit = ? where current = 1', [feuchtigkeit], one=True)

		#### update current db values


		return jsonify(data)


@app.route("/kontroll")
def kontroll():
	# obviously should be taken from input instead
	kontroll_daten = {
		'licht_an': True,
		'licht_auto' : True,
		'ventil_an': True,
		'ventil_auto' : True,
		'befeuchter_an': True,
		'befeuchter_auto' : True,
	}
	kontroll_daten_text = "{'licht_an': True,'licht_auto' : True,'ventil_an': True,'ventil_auto' : True,'befeuchter_an': True,'befeuchter_auto' : True,}"
	return kontroll_daten_text



if __name__ == '__main__':

	app.run(debug=True)

	#subprocess.run(['python','schaltung_2.py'])
