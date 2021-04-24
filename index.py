import requests
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    gas = requests.get(
        'https://api.zapper.fi/v1/gas-price?network=ethereum&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241')
    standard = gas.json()['standard']
    fast = gas.json()['fast']
    instant = gas.json()['instant']
    return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant))


@app.route('/index.html')
def home():
    return render_template('index.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


@app.route('/register.html')
def register():
    return render_template('register.html')


@app.route('/forgot-password.html')
def forgotPassword():
    return render_template('forgot-password.html')


@app.route('/404.html')
def notFound():
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
