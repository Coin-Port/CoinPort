import requests
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from functions import get_transactions, get_curr_balance, get_historical_balance, get_pnl, get_price_history_interval, unix_to_readable
from time import time as curr_time

app = Flask(__name__)

# Ether Balance builder


def chart_builder(address: str):
    my_transactions = get_transactions(address)
    start = int(my_transactions[0]['timeStamp']) - 3600  # first transaction
    end = int(curr_time())
    hist_bal = get_historical_balance(address, my_transactions, start, end)
    time_list = list(hist_bal.keys())
    # pnl = get_pnl(hist_bal, start, end) #pnl function
    tuple_list = []
    for time in hist_bal:
        temp = unix_to_readable(time)
        if end - start <= 86400:  # 1 day or less
            spliced_time = temp[-8:-3]  # time only
        elif end - start <= 518400:  # 60 days or less
            spliced_time = temp[5:-3]  # mm/dd hh/mm
        elif end - start <= 31556952:  # 1 year or less
            spliced_time = temp[5:10]  # mm/dd
        else:  # more than a year
            spliced_time = temp[0:10]  # yy/mm/dd
        #print(time, hist_bal[time])
        tuple_list.append(
            tuple([spliced_time, float(hist_bal[time]['ETH'][0])]))
    return tuple_list

def pie_builder(address: str):
    pie_list = []
    pie_dict = get_curr_balance(address)
    for token in list(pie_dict.keys()):
        if (float(pie_dict[token][1]) > 0):
            pie_list.append(tuple([token, float(pie_dict[token][1])]))
    return pie_list

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
        pie_list = pie_builder(address)
        chart_list = chart_builder(address)
        # reverse chronlogical -> chronlogical and unzips
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        #Pie labels and values
        pie_labels, pie_values = [list(i) for i in list(zip(*pie_list))]
        #print(labels, values)
        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), labels=labels, values=values, address=address, pie_labels=pie_labels, pie_values=pie_values)
    else:
        return render_template('landing.html')


@app.route('/index.html', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        address = request.form["address"]
        print(address)
        chart_list = chart_builder(address)
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        return render_template('index.html', labels=labels, values=values, address="address")
    else:
        return render_template('landing.html')


@app.route('/test.html')
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(debug=True)
