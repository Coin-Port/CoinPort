import json
from urllib import request
from time import strptime, struct_time, time, mktime
from coin_list import coin_list as coingecko_coin_list
from coin_list import supported_protocols as zapper_supported_protocols
from datetime import datetime

#address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9' # my address that i was testing
#address = '0x145c692ea0B7D8dD26F0eD6230b2fC6c44EffdA1' # random address from the list that JC sent
zapper_api_key = '96e0cc51-a62e-42ca-acee-910ea7d2a241' # public use API key
ethscan_api_key = 'JBD58KU8MHIJ374AX3J1ICHX4F64YAKMAD'
covalent_api_key = 'ckey_6c3f3233e25f4ad1bfe6cfc2403'

def unix_to_readable(time: int):
    return datetime.fromtimestamp(time).strftime('%Y/%m/%d %H:%M:%S')

def readable_to_unix(time: int):
    return mktime(struct_time(strptime(time, '%Y/%m/%d %H:%M:%S')))

def get_tokens(address): # current tokens owned by user
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
        return data

# per may 1st, 2021, this function is now deprecated in favor of one purely using etherscan, it's being kept as a comment for possible ideas in the future
#def get_transactions_w_ethscan(address): # historical transactions, with ethscan. im not deleting this function in the case that we will need to use ethscan again.
#    # as of april 28th, 2021, zapper does not record transactions that have a value of 0 ether and/or don't move any tokens around
#    # this is a problem because there are transactions that have a value of 0 eth and do not move tokens around, but they cost gas, and will thus change the value of the account
#    # here are examples of txn's hashes where this will occur:
#    # 0x5a41bcd2d19618cefdc4414d63dec4e5d57758e9c816fbcd1bf28400215691f0 - this transaction approved Dai for trade on Aave, but it is only an approval with no deposit, costing 0.0018 in ETH for gas
#    # 0x0e41dc2eff99f9cc4df325bbde72c9ef09feca49c39d159ca144700e2dba6c32 - this transaction "scanned an asteroid" in the game Influence, costing 0.0015 in ETH for gas
#    with request.urlopen('https://api.zapper.fi/v1/transactions/%s?api_key=%s' % (address, zapper_api_key)) as url: # historical transactions from zapper
#        zapper_data = json.loads(url.read().decode())[::-1] # originally reverse chronological
#    with request.urlopen('https://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s' % (address, ethscan_api_key)) as url: # historical transactions from etherscan
#        ethscan_data = json.loads(url.read().decode()) # already chronological
#        if ethscan_data['status'] != '1':
#            print('error fetching data')
#            return False
#        ethscan_data = ethscan_data['result']#[::-1]
#    # why am i using both?
#    # zapper has easy to parse data but misses transactions
#    # etherscan catches some of the transactions that zapper misses
#    # but, it seems like they both are missing transactions that the other don't have as well..
#
#    txn_hashes = set() # keys will be hashes, two transactions from a user can happen at the same time so timestamp isn't an option
#    # i'll insert hashes into chronological order, then go in that order to make an empty dictionary as dictionaries maintain insertion order
#    # and then keep track of chronlogy with a tuple of hash and timestamp
#    # using a set so there's no repeats
#
#    for txn in zapper_data:
#        txn_hashes.add((int(txn['timeStamp']), txn['hash']))
#
#    for txn in ethscan_data:
#        if (int(txn['timeStamp']), txn['hash']) not in txn_hashes:
#            pass
#            #print(txn['hash'])
#        txn_hashes.add((int(txn['timeStamp']), txn['hash']))
#
#    txn_hashes = [i[1] for i in sorted(list(txn_hashes))] # get only hashes, sorts by the timestamps since they're index 0, so they're in chronological order
#    
#    data = {}
#
#    for hash in txn_hashes:
#        data[hash] = {}
#        data[hash]['onEthscan'] = False
#        data[hash]['isError'] = 0 # assume transaction went through
#
#    for txn in ethscan_data:
#        data[txn['hash']]['symbol'] = 'ETH'
#        data[txn['hash']]['direction'] = 'outgoing' if txn['from'].lower() == address.lower() else 'incoming'
#        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
#        data[txn['hash']]['gas'] = float(txn['gasPrice']) / 1000000000000000000 * float(txn['gasUsed']) # 1 billion * 1 billion because wei -> gwei -> eth
#        data[txn['hash']]['onZapper'] = False # don't know if i'm gonna use this but keeping it just in case
#        data[txn['hash']]['onEthscan'] = True
#        data[txn['hash']]['isError'] = bool(txn['isError'])
#
#    for txn in zapper_data:
#        data[txn['hash']]['symbol'] = txn['symbol']
#        data[txn['hash']]['amount'] = float(txn['amount'])
#        data[txn['hash']]['direction'] = txn['direction']
#        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
#        data[txn['hash']]['subTransactions'] = txn['subTransactions']
#        data[txn['hash']]['gas'] = float(txn['gas'])
#        data[txn['hash']]['onZapper'] = True
#        data[txn['hash']]['isError'] = not bool(txn['txSuccessful'])
#
#    return data

def get_curr_balance_zapper(address: str) -> dict:
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    data = data[address.lower()]
    #print(data)
    balances = dict() #dict that pairs coin symbol to its balance
    for token in data:
        balances[token["symbol"]] = token["balance"]
    return balances

#Returns a list of dicts, a dict for each currency that contains in staking
#symbol: the symbol
#balance: balance in crypto 
#balanceUSD: balance of crypto in USD
def get_staked_zapper(address: str) -> list:
    #There are 4 different protocols for staking so I combine all of them, balances_sub is a list of the balances for each protocol
    protocols = {0 : "masterchef", 1 : "geyser", 2 : "gauge", 3 : "single-staking"}
    balances_main = list()
    balances_sub = list()
    
    data = list()

    symbol_lookup = dict()
    for protocol in protocols:
        with request.urlopen('https://api.zapper.fi/v1/staked-balance/%s?addresses[]=%s&network=ethereum&api_key=%s' % (protocols[protocol], address, zapper_api_key)) as url:
            data.append(json.loads(url.read().decode()))
        data = data[address.lower()]
        if data: 
            data = ["tokens"]
            for token in data:
                balances_sub.append({"symbol" : token["symbol"], "balance" : token["balance"], "balanceUSD" : token["balanceUSD"]})
                if token["symbol"] in symbol_lookup.keys(): symbol_lookup[[token["symbol"]].append(len(balances_sub)-1)
                symbol_lookup[token["symbol"] : [len(balances_sub)-1]] #dict of locations of occurence of a symbol
            balances_sub.sort(key = lambda k: k["symbol"])
    
    for indices in symbol_lookup:
        temp_balance = balances_sub[indices[0]]
        for index in indices[1:]:
            temp_balance["balance"] += balances_sub[index]["balance"]
            temp_balance["balanceUSD"] += balances_sub[index]["balanceUSD"]
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

def revert_txns_zapper(transactions: list, balance: dict, end: int, txn_index: int) -> (int, dict): # returns new txn_index and balance
    # reverts transactions from present until 'end', transactions are given reverse chronologically
    balance = balance.copy() #make a copy of balance to not modify original, but i think either could work
    while int(transactions[txn_index]['timeStamp']) >= end: # the balances would be the same if no transactions take place between the two times
        txn = transactions[txn_index]
        if txn['direction'] == 'exchange' or txn['direction'] == 'outgoing':
            balance['ETH'] += txn['gas'] # add gas since we're reverting
        if txn['txSuccessful']:
            for sub_txn in txn['subTransactions']:
                coin = sub_txn['symbol']
                amount = float(sub_txn['amount'])
                if sub_txn['type'] == 'outgoing':
                    if coin in balance:
                        balance[coin] += amount
                    else:
                        balance[coin] = amount
                elif sub_txn['type'] == 'incoming':
                    if coin in balance:
                        balance[coin] -= amount
                    else:
                        balance[coin] = 0 # for some reason sometimes coins that show up in transactions dont show up on balances
        txn_index += 1
    return (txn_index, balance)

# functions with _eth at the end are ETH only and don't support tokens
# this was made because of some quirks with the Zapper APIs which don't allow us to support tokens yet
def revert_txns_eth(transactions: list, balance: dict, end: int, txn_index: int) -> (int, dict): # returns new txn_index and balance
    # reverts transactions from present until 'end', transactions are given reverse chronologically
    balance = balance.copy() #make a copy of balance to not modify original, but i think either could work
    while txn_index < len(transactions) and int(transactions[txn_index]['timeStamp']) >= end: # the balances would be the same if no transactions take place between the two times
        txn = transactions[txn_index]
        if txn['direction'] == 'exchange' or txn['direction'] == 'outgoing':
            balance['ETH'] += txn['gas'] # add gas since we're reverting
        if txn['txSuccessful']:
            for sub_txn in txn['subTransactions']:
                amount = float(sub_txn['amount'])
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

def get_historical_balance_deprec(address: str, transactions: list, start: int, end: int) -> dict:
    balance = get_curr_balance(address)
    historical_balance = {}
    txn_index = 0

    # using time.time(), a float may be passed in so this is just a precaution
    end = int(end)
    start = int(start)

    if end - start <= 86400: # 1 day or less
        interval = 60 # minutely intervals
    elif end - start <= 5184000: # 60 days or less
        interval = 3600 # hourly intervals    
    else: # more than 60 days
        interval = 86400 # daily intervals

    reverted = revert_txns_zapper(transactions, balance, end, 0) # revert transactions until we reach the end of our interval from the present
    txn_index, historical_balance[end] = reverted[0], reverted[1]

    for time in range(end - interval, start - interval - 1, -interval): # reverse chronological in variable interval
        historical_balance[time] = historical_balance[time + interval] # current balance is temporarily equivalent to prior balance
        reverted = revert_txns_zapper(transactions, historical_balance[time], time, txn_index)
        txn_index, historical_balance[time] = reverted[0], reverted[1]
    
    return historical_balance

def get_historical_balance_eth_only(address: str, transactions: list, start: int, end: int) -> dict: # only ETH
    balance = get_curr_balance_eth(address)
    historical_balance = {}
    txn_index = 0

    # using time.time(), a float may be passed in so this is just a precaution
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
        data = json.loads(url.read().decode())
        return data['prices']

def get_historical_fiat_worth(historical_balance: dict, start: int, end: int) -> dict:
    pass

def get_historical_fiat_worth_eth_only(historical_balance: dict, start: int, end: int, currency: str) -> dict:
    price_history = get_price_history_interval('ETH', start, end, currency)
    fiat_history = {}
    for time, price in zip(historical_balance, price_history): 
        # since the intervals are the same size and the beginning and end are close enough (if not the same)
        # soo.... I can just iterate through these two things side by side and not run into any trouble (hopefully)
        fiat_history[time] = {'ETH': historical_balance[time]['ETH'] * price[1]}
    return fiat_history

def get_pnl(hist_fiat_balance: dict, start: int, end: int) -> tuple: # (pnl, pnl_percent, daily_avg_pnl, daily_avg_pnl_percent)    
    # generalizing for more than just ETH
    start_time = list(hist_fiat_balance)[-1]
    end_time = list(hist_fiat_balance)[0]
    start_val = sum(hist_fiat_balance[start_time].values())
    end_val = sum(hist_fiat_balance[end_time].values())
    
    pnl = end_val - start_val 
    pnl_percent = pnl / start_val * 100 # percentage gain over initial value
    daily_avg_pnl = pnl / ((end_time - start_time) / 864000) # total pnl / number of days
    daily_avg_pnl_percent = daily_avg_pnl / start_val * 100
    return (pnl, pnl_percent, daily_avg_pnl, daily_avg_pnl_percent)

def get_transactions_ethscan(address): # historical transactions with only Etherscan, this is an attempt to write it without dependency on Zapper.
    # will return a dict structured like so:
    # {
    #   hash: { 'timeStamp': int, 
    #           'type': str ('normal', 'internal', 'erc20', 'erc721')
    #           'value': float (value / 1000000000000000000), # 0 if not ETH
    #           'gas': float (gasPrice / 1000000000000000000 * gasUsed), 
    #           'txSuccessful': bool,    
    #           'direction': str ('incoming', 'outgoing'), # not gonna bother with the whole 'exchange' thing, doesn't really make a difference in my use case
    #           'subTransaction': [
    #                               { 'timeStamp': int,
    #                                 'hash': str (hash),
    #                                 'type': str ('incoming', 'outgoing')
    #                                 'tokenName': str,
    #                                 'tokenSymbol': str,
    #                                 'value': float (value / 10**tokenDecimal)
    #                               }, ... next transaction if one exists
    #                             ] if this is empty, then the the transaction is purely ETH
    #           'from': str (address),
    #           'to': str (address) # don't need these, but I'll keep them just because
    #         }
    # } 
    
    def get_txn_type(tx_type):
        parsed_txs = {}
        with request.urlopen('https://api.etherscan.io/api?module=account&action=%s&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s' % (tx_type, address, ethscan_api_key)) as url: # historical transactions from etherscan
            txns = json.loads(url.read().decode()) # chronological order
            if not bool(txns['status']):
                print('error fetching %s, returned status 0' % (tx_type))
                return False
            elif bool(txns['status']):
                return txns['result'] # list of dictionaries
            else:
                print('error fetching %s, no data returned' % (tx_type))
                return False
        
    normal_txns_list = get_txn_type('txlist')
    internal_txns_list = get_txn_type('txlistinternal')
    erc20_txns_list = get_txn_type('tokentx')

    hashes = set() # all unique txn hashes

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

    def parsed_tx(tx: dict, tx_type='normal', symbol='ETH', div=1000000000000000000) -> dict:
        return {
            'timeStamp': int(tx['timeStamp']),
            'humanTime': unix_to_readable(int(tx['timeStamp'])),
            'type': tx_type,
            'symbol': symbol,
            'value': float(tx['value']) / div,
            'gas': float(tx['gasPrice']) / 1000000000000000000 * float(tx['gasUsed']) if 'gasPrice' in tx else 0,
            'txSuccessful': not bool(tx['isError']) if 'isError' in tx else True,
            'direction': 'incoming' if tx['to'].lower() == address.lower() else 'outgoing',
            'subTransaction': [],
            'hash': hash,
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
        if txns[hash]: # txns[hash] != 0
            txns[hash]['subTransaction'].append(tx_parsed)
        else:
            txns[hash] = tx_parsed

    for hash in erc20_txns:
        tx = erc20_txns[hash]
        tx_parsed = parsed_tx(tx, tx_type='erc20', symbol=tx['tokenSymbol'], div=10**int(tx['tokenDecimal']))
        if txns[hash.strip()]:
            txns[hash.strip()]['subTransaction'].append(tx_parsed)
        else:
            txns[hash.strip()] = tx_parsed

    return txns
    
def get_curr_balance(address: str) -> dict:
    return None

def get_historical_balance(txns: dict, start: int, end: int) -> dict:
    # example output:
    # {
    #   start: {'ETH': 3.14159, 'LINK': 2.71828, 'DAI': 1.618033},
    #   start + interval: ...,
    #   ...,
    #   end: ...
    # }

    # precautions
    start = int(start)
    end = int(end)

    hist_bal = {}

    if end - start <= 86400: # 1 day or less
        interval = 60 # minutely intervals
    elif end - start <= 7776000: # 90 days or less
        interval = 3600 # hourly intervals
    else: # more than 90 days
        interval = 86400 # daily intervals
    
    # these intervals are based off of how the CoinGecko API handles requests


    hist_bal[start] = 

    for time in range(start + interval, end + interval):
        pass

