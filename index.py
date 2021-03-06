import requests
from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap
from functions import get_staked_zapper, get_pool_balance_zapper, get_transactions, get_curr_balance, get_historical_balance, get_pnl, get_price_history_interval, unix_to_readable
from time import time as curr_time
import random
from coin_list import coingecko_coin_list

app = Flask(__name__)
app.secret_key = 'super duper secret key!'

address = '0x7e379d280ac80bf9e5d5c30578e165e6c690acc9'

graph_colors = [
    '72539C', # royal purple
    '7B3250', # quinacdridone magenta
    'EE6352', # fire opal
    '127F84', # teal
    '1CFEBA', # sea green crayola
    '6874E8', # neon blue
    '42B9D1', # maximum blue
    'EDAE49', # sunray
    'E5E059', # straw
    'DDF2EB'  # honeydew
]

# Ether Balance builder

def chart_builder(hist_bal: dict, start: int, end: int):
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

def pie_builder(pie_dict: dict):
    pie_list = []
    #pie_dict = get_curr_balance(address)
    for token in list(pie_dict.keys()):
        if (float(pie_dict[token][1]) > 0.001):
            pie_list.append(tuple([token, float(pie_dict[token][1])]))
    return pie_list

def time_splicer(time: int, time_interval: int) -> str:
    temp = unix_to_readable(time)
    if time_interval <= 86400:  # 1 day or less
        return temp[-8:-3]  # time only
    elif time_interval <= 86400 * 30:  # 90 days or less
        return temp[5:-3]  # mm/dd hh/mm
    elif time_interval <= 31556952:  # 1 year or less
        return temp[5:10]  # mm/dd
    else:  # more than a year
        return temp[0:10]  # yy/mm/dd

def value_builder(hist_bal: dict, start: int, end: int):
    # pnl = get_pnl(hist_bal, start, end) #pnl function
    value_list = []
    for time in hist_bal:
        for coin in hist_bal[time]:
            value_list.append(tuple([time_splicer(time, end-start), float(hist_bal[time][coin][1])]))
    return value_list

def get_gas():
    gas = requests.get('https://api.zapper.fi/v1/gas-price?network=ethereum&api_key=96e0cc51-a62e-42ca-acee-910ea7d2a241').json()
    return gas['standard'], gas['fast'], gas['instant']

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('landing.html')

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    start_time = curr_time()
    if request.method == "GET":
        address = request.args.get('address')
        time_interval = request.args.get('times')
        time_variable = 30
        if time_interval == "1wk":
            time_variable = 7
        elif time_interval == "1m":
            time_variable = 30
        elif time_interval == "2m":
            time_variable = 60
        else:
            time_variable = 7

        print('address: ' + address)
        #print(time_variable, time_interval)

        #currency = request.args.get('currency')
        currency = ''
        currency_symbol = '$'

        my_transactions = get_transactions(address)
        if not my_transactions or my_transactions == -1:
            flash('Invalid address, please try again.' if not my_transactions else 'Sorry, we ran into an error! Pease try again in a few minutes.')
            return render_template('landing.html')

        end = int(curr_time())
        days = 60
        start = end - 86400 * days # 86400 seconds per day (approximately)

        balance = get_curr_balance(address)
        total_balance = round(sum(float(balance[i][1]) for i in balance),2)

        hist_bal = get_historical_balance(balance, address, my_transactions, start, end)

        staked_balance = get_staked_zapper(address)
        pool_balance = get_pool_balance_zapper(address)

        standard, fast, instant = get_gas()
        
        #value_list = value_builder(hist_bal, start, end)
        chart_list = chart_builder(hist_bal, start, end)
        pie_list = pie_builder(balance)
        # reverse chronlogical -> chronlogical and unzips
        # total value labels and values
        #value_labels, amounts = [list(i) for i in list(zip(*value_list[::-1]))]
        #time_labels, amounts = [list(i) for i in list(zip(*value_list[::-1]))]

        col_index = 0

        time_labels = [time_splicer(t, end-start) for t in list(hist_bal.keys())[::-1]] # keys are times in epoch time
        fiat_amounts = {'total': []}
        raw_amounts = {}

        for time in list(hist_bal.keys())[::-1]:
            for coin in hist_bal[time]:
                if coin.lower() in coingecko_coin_list: # has price
                    if coin not in fiat_amounts:
                        fiat_amounts[coin] = []
                    if coin not in raw_amounts and coin != 'total':
                        raw_amounts[coin] = []
                    coin_bal = round(float(hist_bal[time][coin][1]),3)
                    fiat_amounts[coin].append(coin_bal)
                    raw_amounts[coin].append(round(float(hist_bal[time][coin][0]),3))
                    if len(fiat_amounts[coin]) == len(fiat_amounts['total']):
                        fiat_amounts['total'][-1] += coin_bal
                    else:
                        fiat_amounts['total'].append(coin_bal)

        parsed_fiat_amounts = []
        
        for coin in fiat_amounts:
            if col_index == len(graph_colors):
                col_index = 0
            parsed_fiat_amounts.append((coin, fiat_amounts[coin], '#' + graph_colors[col_index]))
            col_index += 1

        parsed_raw_amounts = []
        
        for coin in raw_amounts:
            if col_index == len(graph_colors):
                col_index = 0
            parsed_raw_amounts.append((coin, raw_amounts[coin], '#' + graph_colors[col_index]))
            col_index += 1

        print('nothing to see here')
        
        '''
        all_tokens = list([(fiat_amounts[coin][-1], coin) for coin in fiat_amounts])
        
        
        for i in all_tokens:
            if 'ETH' in i or 'total' in i:
                all_tokens.remove(i)


        top_3_tokens = []
        
        for _ in range(3):
            if len(all_tokens) != 0:
                max_token = max(all_tokens)
                top_3_tokens.append(max_token[1])
                all_tokens.remove(max_token)

        #print(top_3_tokens)

        token1, token2, token3 = top_3_tokens

        print('top tokens:', token1, token2, token3)'''

        #Ether labels and values
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]
        #Pie labels and values
        pie_labels, pie_values = [list(i) for i in list(zip(*pie_list))]

        pnl, pnl_percent, daily_avg_pnl, daily_avg_pnl_percent = get_pnl(hist_bal, start, end)

        wallet_balance = total_balance

        print('took %d seconds' % (curr_time() - start_time))
        return render_template('index.html',
                                standard=int(standard),
                                fast=int(fast),
                                instant=int(instant),
                                time_labels=time_labels,
                                total_vals=fiat_amounts['total'],
                                ETH_vals=fiat_amounts['ETH'],
                                labels=labels,
                                token_fiat_vals=parsed_fiat_amounts, # historical token balances
                                token_raw_vals=parsed_raw_amounts, 
                                values=values, # token balances
                                address=address,
                                pie_labels=pie_labels,
                                pie_values=pie_values,
                                currency_symbol=currency_symbol,
                                currency_ticker=currency,
                                total_balance=round(total_balance+staked_balance[0]+pool_balance[0],2),
                                total_pnl=pnl,
                                pnl_percent=pnl_percent,
                                pnl_color='limegreen' if pnl >= 0 else 'lightcoral',
                                daily_avg_pnl=daily_avg_pnl,
                                daily_avg_percent=daily_avg_pnl_percent,
                                wallet_balance=wallet_balance,
                                staked_balance=round(staked_balance[0], 2),
                                pool_balance=round(pool_balance[0], 2)
                               )

# don't think this does anything?
@app.route('/index.html', methods=['POST', 'GET'])
def home():
    return render_template('landing.html')
    '''if request.method == "GET":
        address = request.args.get('address')
        print('address: ' + str(address))
        chart_list = chart_builder(address)
        labels, values = [list(i) for i in list(zip(*chart_list[::-1]))]

        return render_template('index.html', standard=int(standard), fast=int(fast), instant=int(instant), value_labels=value_labels, amounts=amounts, labels=labels, values=values, address=address, pie_labels=pie_labels, pie_values=pie_values)
    else:
        return render_template('landing.html')'''
    

@app.route('/test.html')
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.secret_key = 'super duper secret key!'
    app.run(debug=True)
