import time
from cryptoaddress import EthereumAddress
import json
from urllib import request
from decimal import Decimal
from coin_list import coingecko_coin_list

covalent_api_key = 'ckey_6c3f3233e25f4ad1bfe6cfc2403'


def main():
    print(get_curr_balance("0x7E379d280AC80BF9e5D5c30578e165e6c690acC9"))


def get_curr_balance(address: str, chain_id=1, currency='usd'):
    balance = {}

    if chain_id not in [1, 137, 80001, 56, 43114, 43113, 250]:
        print('invalid chain id')
        return False

    # https://api.covalenthq.com/v1/1/address/0x7E379d280AC80BF9e5D5c30578e165e6c690acC9/balances_v2/?&key=ckey_6c3f3233e25f4ad1bfe6cfc2403
    with request.urlopen(request.Request("https://api.covalenthq.com/v1/%d/address/%s/balances_v2/?&key=%s" % (chain_id, address, covalent_api_key), headers={'User-Agent': 'Mozilla/5.0'})) as url:
        data = json.loads(url.read().decode())
    data = data['data']['items']

    calls_made = 0

    for item in data:
        amount = Decimal(item['balance']) / 10**int(item['contract_decimals'])
        symbol = item['contract_ticker_symbol'].lower()
        price = item['quote']
        if calls_made < 60 and price !=0: # max 60 calls per minute on coingecko
            calls_made += 1
            print(symbol,price)
        else:
            price = 0
        balance[item['contract_ticker_symbol']] = [amount, amount * Decimal(price)]

    return balance



if __name__ == "__main__":
    main()
