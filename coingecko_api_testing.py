import json
from urllib import request

def get_price_history(coin_id: str, days: str, currency: str):
    interval = 'daily'

    if int(days) <= 60: # hourly price intervals for past 2 months
        interval = 'hourly'
    elif int(days) <= 1: # minute price interval for past day
        interval = 'minutely' 

    with request.urlopen('https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=%s&days=%s&interval=%s' % (coin_id, currency, days, interval)) as url:
        data = json.loads(url.read().decode())
        return data

        