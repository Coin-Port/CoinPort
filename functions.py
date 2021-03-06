import json
from urllib import request
from time import strptime, struct_time, time, mktime
from coin_list import coingecko_coin_list
from coin_list import supported_protocols as zapper_supported_protocols
from datetime import datetime
from decimal import Decimal
import cryptoaddress

#address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9' # my address that i was testing
#address = '0x145c692ea0B7D8dD26F0eD6230b2fC6c44EffdA1' # random address from the list that JC sent
zapper_api_key = '96e0cc51-a62e-42ca-acee-910ea7d2a241' # public use API key
ethscan_api_key = 'JBD58KU8MHIJ374AX3J1ICHX4F64YAKMAD'
covalent_api_key = 'ckey_6c3f3233e25f4ad1bfe6cfc2403'

def unix_to_readable(time: int):
    return datetime.fromtimestamp(time).strftime('%Y/%m/%d %H:%M:%S')

def day_to_unix(time: str):
    return datetime.fromtimestamp(time).strftime('%Y/%m/%d')

def readable_to_unix(time: int):
    return mktime(struct_time(strptime(time, '%Y/%m/%d %H:%M:%S')))

def get_tokens(address): # current tokens owned by user
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
        return data

#Gets the current balance of an address using zappper
def get_curr_balance_zapper(address: str) -> dict:
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    data = data[address.lower()]
    #print(data)
    balances = dict() #dict that pairs coin symbol to its balance
    for token in data:
        balances[token["symbol"]] = token["balance"]
    return balances

#Gets the current balance of pools using zapper
#Returns a list of dicts where each dict has, except the first element in the list which is the total balanceUSD of all pools:
#symbol: the symbol of the pool
#balanceUSD: the total balance in usd user has in the pool
#balances1: the balance of the first type of crypto where s1 is the symbol (eg balanceeth, balancebtc)
#balances2: the balance of the second type of crypto where s2 is the symbol (eg balancebtc, balanceeth)
def get_pool_balance_zapper(address: str) -> dict:
    protocols_with_pools = get_pool_protocols_zapper(address)
    data = list()
    balances = list()
    balances.append(0)

    for protocol in protocols_with_pools:
        with request.urlopen('https://api.zapper.fi/v1/protocols/%s/balances?addresses[]=%s&network=ethereum&api_key=%s' % (protocol, address, zapper_api_key)) as url:
            data.append(json.loads(url.read().decode())[address.lower()]["products"])

    if (len(data)==0): return [0]
    data = data[0]

    for pool in data:
        if "assets" in pool:
            for asset in pool["assets"]:
                balances[0] += asset["balanceUSD"]
                to_append = {"symbol" : asset["symbol"], "balanceUSD" : asset["balanceUSD"]}
                if "tokens" in asset:
                    for token in asset["tokens"]:
                        balance_symbol = "balance" + token["symbol"]
                        to_append[balance_symbol] = token["balance"]
                balances.append(to_append)

    return balances

#Helper function for get_pool_balance_zapper(), used to find what protocols we have to loop over
def get_pool_protocols_zapper(address: str) -> list:
    protocols_with_pools = list()
    with request.urlopen('https://api.zapper.fi/v1/protocols/balances/supported?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    for network in data:
        if "network" in network and network["network"]=="ethereum":
            data = network["protocols"]
            break
    for protocol in data:
        if "meta" in protocol.keys() and "tags" in protocol["meta"].keys() and "liquidity-pool" in protocol["meta"]["tags"]: protocols_with_pools.append(protocol["protocol"])

    return protocols_with_pools


#Returns a list of dicts, a dict for each currency that contains in staking, but the first value is total staked balance
#symbol: the symbol
#balance: balance in crypto
#balanceUSD: balance of crypto in USD
def get_staked_zapper(address: str) -> list:
    #There are 4 different protocols for staking so I combine all of them, balances_sub is a list of the balances for each protocol
    protocols = {0 : "masterchef", 1 : "geyser", 2 : "gauge", 3 : "single-staking"}
    balances_main = list()
    balances_main.append(0)
    balances_sub = list()

    symbol_lookup = dict()
    for protocol in protocols:
        with request.urlopen('https://api.zapper.fi/v1/staked-balance/%s?addresses[]=%s&network=ethereum&api_key=%s' % (protocols[protocol], address, zapper_api_key)) as url:
            data = json.loads(url.read().decode())
        data = data[address.lower()]
        if data:
            data = data[0]["tokens"]
            for token in data:
                balances_sub.append({"symbol" : token["symbol"], "balance" : token["balance"], "balanceUSD" : token["balanceUSD"]})
                if token["symbol"] in symbol_lookup.keys():
                    symbol_lookup[token["symbol"]] = symbol_lookup[token["symbol"]].append(len(balances_sub)-1)
                else:
                    symbol_lookup[token["symbol"]] = [len(balances_sub)-1] #dict of locations of occurence of a symbol
            balances_sub.sort(key = lambda k: k["symbol"])

    for indices in symbol_lookup:
        temp_balance = balances_sub[symbol_lookup[indices][0]]
        for index in symbol_lookup[indices][1:]:
            temp_balance["balance"] += balances_sub[index]["balance"]
            temp_balance["balanceUSD"] += balances_sub[index]["balanceUSD"]
        balances_main[0] += temp_balance["balanceUSD"]
        balances_main.append(temp_balance)

    return balances_main

def get_curr_balance_eth_only(address: str) -> dict:
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    data = data[address.lower()]
    for token in data:
        if token['symbol'] == 'ETH': return {'ETH': token['balance']} # only ETH balance

#def get_transactions(address: str) -> list:
#    with request.urlopen('https://api.zapper.fi/v1/transactions/%s?api_key=%s' % (address, zapper_api_key)) as url: # historical transactions from zapper
#        data = json.loads(url.read().decode())
#    return data

# functions with _eth at the end are ETH only and don't support tokens
# this was made because of some quirks with the Zapper APIs which don't allow us to support tokens yet
def revert_txns_eth(transactions: list, balance: dict, end: int, txn_index: int) -> tuple: # returns new txn_index and balance
    # reverts transactions from present until 'end', transactions are given reverse chronologically
    balance = balance.copy() #make a copy of balance to not modify original, but i think either could work
    while txn_index < len(transactions) and int(transactions[txn_index]['timeStamp']) >= end: # the balances would be the same if no transactions take place between the two times
        txn = transactions[txn_index]
        if txn['direction'] == 'exchange' or txn['direction'] == 'outgoing':
            balance['ETH'] += txn['gas'] # add gas since we're reverting
        if txn['txSuccessful']:
            for sub_txn in txn['subTransactions']:
                amount = Decimal(sub_txn['amount'])
                if sub_txn['symbol'] == 'ETH':
                    if sub_txn['type'] == 'outgoing':
                        if 'ETH' in balance:
                            balance['ETH'] += amount
                        else:
                            balance['ETH'] = amount
                    elif sub_txn['type'] == 'incoming':
                        if 'ETH' in balance:
                            balance['ETH'] -= amount
                        else: # if some how the user has sent ETH but ETH doesn't exist in their wallet I'll just set it to 0
                            balance['ETH'] = 0
        txn_index += 1
    return (txn_index, balance)

def get_historical_balance_eth_only(address: str, transactions: list, start: int, end: int) -> dict: # only ETH
    balance = get_curr_balance_eth_only(address)
    historical_balance = {}
    txn_index = 0

    # using time.time(), a Decimal may be passed in so this is just a precaution
    end = int(end)
    start = int(start)

    # This is from the coingecko API documentation
    # see here: https://www.coingecko.com/api/documentations/v3#/coins/get_coins__id__market_chart
    # Data granularity is automatic (cannot be adjusted)
    # 1 day from query time = 5 minute interval data
    # 1 - 90 days from query time = hourly data
    # above 90 days from query time = daily data (00:00 UTC)

    if end - start <= 86400: # 1 day or less
        interval = 360 # 5-minutely intervals
    elif end - start <= 7776000: # 90 days or less
        interval = 3600 # hourly intervals
    else: # more than 90 days
        interval = 86400 # daily intervals

    reverted = revert_txns_eth(transactions, balance, end, 0) # revert transactions until we reach the end of our interval from the present
    txn_index, historical_balance[end] = reverted[0], reverted[1]

    for time in range(end - interval, start - interval - 1, -interval): # reverse chronological in variable interval
        historical_balance[time] = historical_balance[time + interval].copy() # current balance is temporarily equivalent to prior balance
        reverted = revert_txns_eth(transactions, historical_balance[time], time, txn_index)
        txn_index, historical_balance[time] = reverted[0], reverted[1]

    return historical_balance

def get_price_history(coin_id: str, days: str, currency: str): # I don't think this function needs to be used but I'll keep it just in case
    interval = 'daily'

    if int(days) <= 60: # hourly price intervals for past 2 months
        interval = 'hourly'
    elif int(days) <= 1: # minute price interval for past day
        interval = 'minutely'

    with request.urlopen('https://api.coingecko.com/api/v3/coins/%s/market_chart?vs_currency=%s&days=%s&interval=%s' % (coin_id, currency, days, interval)) as url:
        data = json.loads(url.read().decode())
        return data

def get_price_history_interval(coin_symbol: str, start: int, end: int, currency: str):
    coin_id = coingecko_coin_list[coin_symbol.lower()]['id']

    # This is from the coingecko API documentation
    # see here: https://www.coingecko.com/api/documentations/v3#/coins/get_coins__id__market_chart
    # Data granularity is automatic (cannot be adjusted)
    # 1 day from query time = 5 minute interval data
    # 1 - 90 days from query time = hourly data
    # above 90 days from query time = daily data (00:00 UTC)

    with request.urlopen("https://api.coingecko.com/api/v3/coins/%s/market_chart/range?vs_currency=%s&from=%d&to=%d" % (coin_id, currency, start, end)) as url:
        return {int(time/1000):price for time, price in json.loads(url.read().decode())['prices']}
        # i is epoch time in milliseconds
        # price is price in whatever currency

def get_price_history_interval_list(coin_symbol: str, start: int, end: int, currency: str):
    coin_id = coingecko_coin_list[coin_symbol.lower()]['id']
    with request.urlopen("https://api.coingecko.com/api/v3/coins/%s/market_chart/range?vs_currency=%s&from=%d&to=%d" % (coin_id, currency, start, end)) as url:
        return [price for _, price in json.loads(url.read().decode())['prices']]

def get_historical_fiat_worth_eth_only(historical_balance: dict, start: int, end: int, currency: str) -> dict:
    price_history = get_price_history_interval('ETH', start, end, currency)
    fiat_history = {}
    for time, price in zip(historical_balance, price_history.values()):
        # since the intervals are the same size and the beginning and end are close enough (if not the same)
        # soo.... I can just iterate through these two things side by side and not run into any trouble (hopefully)
        fiat_history[time] = {'ETH': historical_balance[time]['ETH'] * price}
    return fiat_history

# gonna have to rewrite this at some point lul
#Yeah there are a lot of /0 erros here, I put a case at the top that just returns a tuple of 0s if a /0 would happen
def get_pnl(hist_fiat_balance: dict, start: int, end: int) -> tuple: # (pnl, pnl_percent, daily_avg_pnl, daily_avg_pnl_percent)
    # generalizing for more than just ETH
    start_time = list(hist_fiat_balance)[-1]
    end_time = list(hist_fiat_balance)[0]
    start_bal = hist_fiat_balance[start_time]
    end_bal = hist_fiat_balance[end_time]
    start_val = float(sum(start_bal[coin][1] for coin in start_bal))
    end_val = float(sum(end_bal[coin][1] for coin in end_bal))

    if (start_val == 0): start_val = 1

    pnl = end_val - start_val
    pnl_percent = pnl / start_val * 100 # percentage gain over initial value
    daily_avg_pnl = pnl / ((end_time - start_time) / 86400) # total pnl / number of days
    daily_avg_pnl_percent = daily_avg_pnl / start_val * 100
    return (round(i,2) for i in (pnl, pnl_percent, daily_avg_pnl, daily_avg_pnl_percent))

def get_transactions(address): # historical transactions with only Etherscan, this is an attempt to write it without dependency on Zapper.
    # this function essentially combines the normal, internal and erc20 transactions from Etherscan
    # it will take that data and then "clean it up" so that it's easier to deal with later
    # will return a tuple of dicts structured like so:
    # (
    #   { 'hash': str (hash),
    #     'timeStamp': int,
    #     'type': str ('normal', 'internal', 'erc20', 'erc721')
    #     'value': Decimal (value / 1000000000000000000), # 0 if not ETH
    #     'gas': Decimal (gasPrice / 1000000000000000000 * gasUsed),
    #     'txSuccessful': bool,
    #     'direction': str ('incoming', 'outgoing'), # not gonna bother with the whole 'exchange' thing, doesn't really make a difference in my use case
    #     'subTransaction': [
    #                         { 'timeStamp': int,
    #                           'hash': str (hash),
    #                           'type': str ('incoming', 'outgoing')
    #                           'tokenName': str,
    #                           'tokenSymbol': str,
    #                           'value': Decimal (value / 10**tokenDecimal)
    #                         }, ... next transaction if one exists
    #                       ] if this is empty, then the the transaction is purely ETH
    #     'from': str (address),
    #     'to': str (address) # don't need these, but I'll keep them just because
    #   }, ...
    # )
    # it is returned in chronlogical order, i.e. txns[i+1]['timeStamp'] >= txns[i]['timeStamp']

    if address == '':
        return 0

    try:
        cryptoaddress.EthereumAddress(address)
    except ValueError:
        return 0 # invalid address

    def get_txn_type(tx_type):
        parsed_txs = {}
        try:
            with request.urlopen('https://api.etherscan.io/api?module=account&action=%s&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s' % (tx_type, address, ethscan_api_key)) as url: # historical transactions from etherscan
                txns = json.loads(url.read().decode()) # chronological order
                if txns['result'] == 'Max rate limit reached':
                    return 0
                else:
                    return txns['result']
        except:
            return -2 # service unavailable or some other error

    normal_txns_list = get_txn_type('txlist')
    internal_txns_list = get_txn_type('txlistinternal')
    erc20_txns_list = get_txn_type('tokentx')

    if -2 in (normal_txns_list, internal_txns_list, erc20_txns_list):
        return -1 # something's unavailable

    if not normal_txns_list and not internal_txns_list and not erc20_txns_list:
        return -1 # api limit reached

    hashes = set() # all unique txn hashes

    for txn in normal_txns_list + internal_txns_list + erc20_txns_list:
        hashes.add((int(txn['timeStamp']), txn['hash'])) # using timestamp to sort chronlogically

    for txn in normal_txns_list + internal_txns_list + erc20_txns_list:
        hashes.add((int(txn['timeStamp']), txn['hash'])) # using timestamp to sort chronlogically

    hashes = list(h[1] for h in sorted(list(hashes))) # hashes in chronlogical order

    def tx_list_to_dict(tx_list: list) -> dict:
        tx_dict = {}
        for tx in tx_list: # tx is a dict
            if tx['hash'] not in tx_dict:
                tx_dict[tx['hash']] = tx
            else:
                tx_dict[tx['hash'] + ' '] = tx # circumventing unique keys by striping these bad boys later
        return tx_dict

    normal_txns = tx_list_to_dict(normal_txns_list)
    internal_txns = tx_list_to_dict(internal_txns_list)
    erc20_txns = tx_list_to_dict(erc20_txns_list)

    txns = {} # does not include ERC721 txs but who's counting

    def parsed_tx(tx: dict, tx_type='normal', symbol='ETH', name="Ethereum", div=1000000000000000000) -> dict:
        if tx_type == 'internal' or tx_type == 'normal':
            successful = not int(tx['isError'])
        else:
            successful = True
        return {
            'hash': hash,
            'timeStamp': int(tx['timeStamp']),
            'humanTime': unix_to_readable(int(tx['timeStamp'])),
            'name': name,
            'type': tx_type,
            'symbol': symbol,
            'amount': Decimal(tx['value']) / div,
            'gas': Decimal(tx['gasPrice']) / 1000000000000000000 * Decimal(tx['gasUsed']) if 'gasPrice' in tx else 0,
            'txSuccessful': successful,
            'direction': 'incoming' if tx['to'].lower() == address.lower() else 'outgoing',
            'subTransactions': [],
            'from': tx['from'],
            'to': tx['to']
        }

    for hash in hashes:
        if hash in normal_txns: # same as in keys but this one is O(1) search time rather than O(n)
            txns[hash] = parsed_tx(normal_txns[hash])
        else:
            txns[hash] = 0

    for hash in internal_txns:
        tx_parsed = parsed_tx(internal_txns[hash], tx_type='internal')
        if txns[hash.strip()]: # txns[hash] != 0
            txns[hash.strip()]['subTransactions'].append(tx_parsed)
        else:
            txns[hash.strip()] = tx_parsed

    for hash in erc20_txns:
        tx = erc20_txns[hash]
        tx_parsed = parsed_tx(tx, tx_type='erc20', symbol=tx['tokenSymbol'], div=10**int(tx['tokenDecimal']))
        if txns[hash.strip()]:
            txns[hash.strip()]['subTransactions'].append(tx_parsed)
        else:
            txns[hash.strip()] = tx_parsed

    return list(txns.values()) # the dictionary keys were a ruse all along

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

def revert_txns(transactions: list, balance: dict, end: int, txn_index: int): # returns new txn_index and balance
    # reverts transactions from present until 'end', transactions are given reverse chronologically
    balance = balance.copy() #make a copy of balance to not modify original, but i think either could work
    while txn_index < len(transactions) and int(transactions[txn_index]['timeStamp']) >= end: # the balances would be the same if no transactions take place between the two times
        txn = transactions[txn_index]
        if txn['direction'] == 'outgoing':
            balance['ETH'][0] += txn['gas'] # add gas since we're reverting
        if txn['txSuccessful']:
            balance[txn['symbol']][0] += txn['amount'] if txn['direction'] == 'outgoing' else -txn['amount']
            for sub_txn in txn['subTransactions']:
                coin = sub_txn['symbol']
                amount = Decimal(sub_txn['amount'])
                if sub_txn['direction'] == 'outgoing':
                    if coin in balance:
                        balance[coin][0] += amount
                    else:
                        balance[coin] = [amount, 0]
                elif sub_txn['direction'] == 'incoming':
                    if coin in balance:
                        balance[coin][0] -= amount
        txn_index += 1
    return (txn_index, balance)

def get_historical_balance(balance: dict, address: str, txns: list, start: int, end: int, currency='USD'):
    # example output:
    # {
    #   start: {'ETH': [3.14159, 4536.2348], 'LINK': [2.71828, 294.34332], 'DAI': [1.618033, 1.618129]},
    #   start + interval: ...,
    #   ...,
    #   end: ...
    # }

    #balance = get_curr_balance(address)
    historical_balance = {}
    txn_index = 0

    # precautions
    start = int(start)
    end = int(end)

    txns = txns[::-1] # chronological -> reverse chronlogical

    if end - start <= 86400: # 1 day or less
        interval = 300 # 5 minute intervals
    elif end - start <= 7776000: # 90 days or less
        interval = 3600 # hourly intervals
    else: # more than 90 days
        interval = 86400 # daily intervals

    '''
    # round to nearest interval
    new_start = round(start / interval) * interval
    new_end = round(end / interval) * interval

    # within bounds
    start = new_start + interval if new_start < start else new_start
    end = new_end - interval if new_end > end else new_end
    '''

    historical_prices = {'ETH': get_price_history_interval_list('ETH', start, end + interval, currency)[::-1]}

    reverted = revert_txns(txns, balance, end, 0) # revert transactions until we reach the end of our interval from the present
    txn_index, historical_balance[end] = reverted[0], reverted[1]

    for time, index in zip(range(end - interval, start - interval, -interval), range(len(historical_prices['ETH']))): # reverse chronological in variable interval
        # historical_balance[time] = historical_balance[time + interval].copy() # current balance is temporarily equivalent to prior balance
        historical_balance[time] = {}
        for coin in historical_balance[time + interval]:
            historical_balance[time][coin] = historical_balance[time + interval][coin].copy() # copy all the lists to not modify original
        reverted = revert_txns(txns, historical_balance[time], time, txn_index)
        txn_index, historical_balance[time] = reverted[0], reverted[1]
        for coin in historical_balance[time]:
            if coin not in historical_prices:
                if coin.lower() in coingecko_coin_list:
                    historical_prices[coin] = get_price_history_interval_list(coin.lower(), start - interval // 2, end + interval // 2, currency)[::-1]
                else:
                    historical_prices[coin] = [0 for _ in range(len(historical_prices['ETH']))] # set value to 0 if not found
            index2 = index
            while index2 >= len(historical_prices[coin]): index2 -= 1 # temporary fix
            historical_balance[time][coin][1] = historical_balance[time][coin][0] * Decimal(historical_prices[coin][index2])

    return historical_balance

def human_time_hist_bal(hist_bal: dict):
    return {unix_to_readable(time):bal for time, bal in zip(hist_bal.keys(), hist_bal.values())}
