import requests
from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap
from functions import get_transactions, get_curr_balance, get_historical_balance, get_pnl, get_price_history_interval, unix_to_readable
from time import time as curr_time

app = Flask(__name__)

address = '0x7e379d280ac80bf9e5d5c30578e165e6c690acc9'

# Ether Balance builder

def chart_builder(address: str, start: int, end: int):
    my_transactions = get_transactions(address)
    hist_bal = get_historical_balance(address, my_transactions, start, end)
    time_list = list(hist_bal.keys())
    # pnl = get_pnl(hist_bal, start, end) #pnl function
    tuple_list = []
    for time in hist_bal:
        temp = unix_to_readable(time)
        if end - start <= 86400:  # 1 day or less
            spliced_time = temp[-8:-3]  # time only
        elif end - start <= 5184000:  # 60 days or less
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
        if (float(pie_dict[token][1]) > 0.001):
            pie_list.append(tuple([token, float(pie_dict[token][1])]))
    return pie_list

def value_builder(address: str, start: int, end: int):
    my_transactions = get_transactions(address)
    if not my_transactions or my_transactions == -1:
        return my_transactions # error
    hist_bal = get_historical_balance(address, my_transactions, start, end)
    # pnl = get_pnl(hist_bal, start, end) #pnl function
    value_list = []
    for time in hist_bal:
        temp = unix_to_readable(time)
        if end - start <= 86400:  # 1 day or less
            spliced_time = temp[-8:-3]  # time only
        elif end - start <= 5184000:  # 60 days or less
            spliced_time = temp[5:-3]  # mm/dd hh/mm
        elif end - start <= 31556952:  # 1 year or less
            spliced_time = temp[5:10]  # mm/dd
        else:  # more than a year
            spliced_time = temp[0:10]  # yy/mm/dd
        #print(time, hist_bal[time])
        value_list.append(tuple([spliced_time, float(hist_bal[time]['totalValue'])]))
    return value_list

def get_gas():
    gas = requests.get('https://api.zapper.fi/v1/gas-price?network=ethereum&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241').json()
    return gas['standard'], gas['fast'], gas['instant']

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('landing.html')

    '''if request.method == "GET":
        address = request.args.get('address')
        print('address: ' + address)
        end = int(curr_time())
        start = end - 86400 * 30 # 30 days
        value_list = value_builder(address, start, end)
        if not value_list or value_list == -1: # invalid address
            flash('Invalid address, try again.' if not value_list else 'Internal error, please try again in a few minutes.')
            return render_template('landing.html')
        chart_list = chart_builder(address, start, end)
        pie_list = pie_builder(address)
        # reverse chronlogical -> chronlogical and unzips
        # total value labels and values
        value_labels, amounts = [list(i) for i in list(zip(*value_list[::-1]))]
        #Ether labels and values
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        #Pie labels and values
        pie_labels, pie_values = [list(i) for i in list(zip(*pie_list))]
        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), value_labels=value_labels, amounts=amounts, labels=labels, values=values, address=address, pie_labels=pie_labels, pie_values=pie_values)
    '''        

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    if request.method == "GET":
        standard, fast, instant = get_gas()
        address = request.args.get('address')
        print('address: ' + address)
        end = int(curr_time())
        start = end - 86400 * 30 # 30 days
        value_list = value_builder(address, start, end)
        if not value_list or value_list == -1: # invalid address
            flash('Invalid address, please try again.' if not value_list else 'Sorry, we ran into an error! Pease try again in a few minutes.')
            return render_template('landing.html')
        chart_list = chart_builder(address, start, end)
        pie_list = pie_builder(address)
        # reverse chronlogical -> chronlogical and unzips
        # total value labels and values
        value_labels, amounts = [list(i) for i in list(zip(*value_list[::-1]))]
        #Ether labels and values
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        #Pie labels and values
        pie_labels, pie_values = [list(i) for i in list(zip(*pie_list))]
        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), value_labels=value_labels, amounts=amounts, labels=labels, values=values, address=address, pie_labels=pie_labels, pie_values=pie_values)

# don't think this does anything?
@app.route('/index.html', methods=['POST', 'GET'])
def home():
    if request.method == "GET":
        address = request.args.get('address')
        print('address: ' + str(address))
        chart_list = chart_builder(address)
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), value_labels=value_labels, amounts=amounts, labels=labels, values=values, address=address, pie_labels=pie_labels, pie_values=pie_values)
    else:
        return render_template('landing.html')

@app.route('/test.html')
def test():
    return render_template('test.html')


if __name__ == "__main__":
    app.secret_key = 'super duper secret key!'
    app.run(debug=True)
