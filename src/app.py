from flask import Flask, redirect, url_for, render_template, Markup
#import threading

app = Flask(__name__)

# event = threading.event

@app.route("/")
def index():
	return render_template("index.html")


if __name__ == '__main__':
	app.run(debug=True)
