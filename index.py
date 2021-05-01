import requests
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from functions import get_transactions, get_historical_balance_eth, unix_to_readable, get_pnl
from time import time as current_time_float

app = Flask(__name__)

def current_time():
    return int(current_time_float())

@app.route('/', methods=['POST', 'GET'])
def index():
    gas = requests.get(
        'https://api.zapper.fi/v1/gas-price?network=ethereum&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241')
    standard = gas.json()['standard']
    fast = gas.json()['fast']
    instant = gas.json()['instant']

    if request.method == "POST":
        address = request.form["address"]
        print(address)
        my_transactions = get_transactions(address)
        start = int(my_transactions[-1]['timeStamp']) - 3600 # 1 hour before first transaction
        end = current_time()
        hist_bal = get_historical_balance_eth(address, my_transactions, start, end)
        pnl = get_pnl(hist_bal, start, end) #pnl function
        tuple_list = []
        for time in hist_bal:
            temp = unix_to_readable(time)
            if end - start <= 86400: # 1 day or less
                spliced_time = temp[-8:-3] # time only
            elif end - start <= 518400: # 60 days or less
                spliced_time = temp[5:-3] # mm/dd hh/mm
            elif end - start <= 31556952: # 1 year or less
                spliced_time = temp[5:10] # mm/dd
            else: # more than a year
                spliced_time = temp[0:10] # yy/mm/dd
            tuple_list.append(tuple([spliced_time, hist_bal[time]['ETH']]))
        #print(tuple_list)        
        labels, values = [list(i) for i in list(zip(*tuple_list[::-1]))] # reverse chronlogical -> chronlogical and unzips
        #print(labels, values)
        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), labels=labels, values=values, address=address)
    else:
        return render_template('landing.html')

@app.route('/index.html')
def home():
    return render_template('index.html', address="address")

if __name__ == "__main__":
    app.run(debug=True)
