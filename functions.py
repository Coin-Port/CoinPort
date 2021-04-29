import json
from urllib import request
import time

#address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9' # my address that i was testing
#address = '0x145c692ea0B7D8dD26F0eD6230b2fC6c44EffdA1' # random address from the list that JC sent
address = input('address: ')
zapper_api_key = '96e0cc51-a62e-42ca-acee-910ea7d2a241' # public use API key
ethscan_api_key = 'JBD58KU8MHIJ374AX3J1ICHX4F64YAKMAD'

def get_tokens(address): # current tokens owned by user
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
        return data

def get_transactions_w_ethscan(address): # historical transactions, with ethscan. im not deleting this function in the case that we will need to use ethscan again.
    # as of april 28th, 2021, zapper does not record transactions that have a value of 0 ether and/or don't move any tokens around
    # this is a problem because there are transactions that have a value of 0 eth and do not move tokens around, but they cost gas, and will thus change the value of the account
    # here are examples of txn's hashes where this will occur:
    # 0x5a41bcd2d19618cefdc4414d63dec4e5d57758e9c816fbcd1bf28400215691f0 - this transaction approved Dai for trade on Aave, but it is only an approval with no deposit, costing 0.0018 in ETH for gas
    # 0x0e41dc2eff99f9cc4df325bbde72c9ef09feca49c39d159ca144700e2dba6c32 - this transaction "scanned an asteroid" in the game Influence, costing 0.0015 in ETH for gas
    with request.urlopen('https://api.zapper.fi/v1/transactions/%s?api_key=%s' % (address, zapper_api_key)) as url: # historical transactions from zapper
        zapper_data = json.loads(url.read().decode())[::-1] # originally reverse chronological
    with request.urlopen('https://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s' % (address, ethscan_api_key)) as url: # historical transactions from etherscan
        ethscan_data = json.loads(url.read().decode()) # already chronological
        if ethscan_data['status'] != '1':
            print('error fetching data')
            return False
        ethscan_data = ethscan_data['result']#[::-1]
    # why am i using both?
    # zapper has easy to parse data but misses transactions
    # etherscan catches some of the transactions that zapper misses
    # but, it seems like they both are missing transactions that the other don't have as well..

    txn_hashes = set() # keys will be hashes, two transactions from a user can happen at the same time so timestamp isn't an option
    # i'll insert hashes into chronological order, then go in that order to make an empty dictionary as dictionaries maintain insertion order
    # and then keep track of chronlogy with a tuple of hash and timestamp
    # using a set so there's no repeats

    for txn in zapper_data:
        txn_hashes.add((int(txn['timeStamp']), txn['hash']))

    for txn in ethscan_data:
        if (int(txn['timeStamp']), txn['hash']) not in txn_hashes:
            pass
            #print(txn['hash'])
        txn_hashes.add((int(txn['timeStamp']), txn['hash']))

    txn_hashes = [i[1] for i in sorted(list(txn_hashes))] # get only hashes, sorts by the timestamps since they're index 0, so they're in chronological order
    
    data = {}

    for hash in txn_hashes:
        data[hash] = {}
        data[hash]['onEthscan'] = False
        data[hash]['isError'] = 0 # assume transaction went through

    for txn in ethscan_data:
        data[txn['hash']]['symbol'] = 'ETH'
        data[txn['hash']]['direction'] = 'outgoing' if txn['from'].lower() == address.lower() else 'incoming'
        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
        data[txn['hash']]['gas'] = float(txn['gasPrice']) / 1000000000000000000 * float(txn['gasUsed']) # 1 billion * 1 billion because wei -> gwei -> eth
        data[txn['hash']]['onZapper'] = False # don't know if i'm gonna use this but keeping it just in case
        data[txn['hash']]['onEthscan'] = True
        data[txn['hash']]['isError'] = bool(txn['isError'])

    for txn in zapper_data:
        data[txn['hash']]['symbol'] = txn['symbol']
        data[txn['hash']]['amount'] = float(txn['amount'])
        data[txn['hash']]['direction'] = txn['direction']
        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
        data[txn['hash']]['subTransactions'] = txn['subTransactions']
        data[txn['hash']]['gas'] = float(txn['gas'])
        data[txn['hash']]['onZapper'] = True
        data[txn['hash']]['isError'] = not bool(txn['txSuccessful'])

    return data


def get_balance_w_ethscan(transactions: dict, time: int) -> dict: # another function that will likely be unused but this is back up in the case that Zapper is unable to fix the missing transactions
    user_bal = {'ETH': 0}

    for txn_hash in transactions:
        txn = transactions[txn_hash]
        #print('new transaction:')
        #print(txn_hash, txn['timeStamp'])
        if int(txn['timeStamp']) > time:
            return user_bal

        if not txn['isError']:
            if 'subTransactions' in txn.keys():
                sub_txn = txn['subTransactions']
                for sub in sub_txn:
                    coin = sub['symbol']
                    amount = float(sub['amount'])
                    if sub['type'] == 'incoming' :
                        if coin in user_bal.keys():
                            user_bal[coin] += amount
                        else:
                            user_bal[coin] = amount
                        #print('added %f %s' % (amount, coin))
                    if sub['type'] == 'outgoing': 
                        if coin in user_bal.keys():
                            user_bal[coin] -= amount
                        else:
                            user_bal[coin] = amount
                        #print('removed %f %s' % (amount, coin))
                    #print(amount, coin, sub['type'], user_bal)

        if (txn['direction'] != 'incoming'): # only paying for gas if outgoing
            user_bal['ETH'] -= float(txn['gas'])
            #print('used %f gas' % (float(txn['gas'])))

        #print(user_bal)
        #print('')
    return user_bal

def get_curr_balance(address: str) -> dict:
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    data = data[address.lower()]
    #print(data)
    balances = dict() #dict that pairs coin symbol to its balance
    for token in data:
        balances[token["symbol"]] = token["balance"]
    return balances

def get_curr_balance_eth(address: str) -> dict:
    with request.urlopen('https://api.zapper.fi/v1/balances/tokens?addresses[]=%s&api_key=%s' % (address, zapper_api_key)) as url:
        data = json.loads(url.read().decode())
    data = data[address.lower()]
    for token in data:
        if token['symbol'] == 'ETH': return {'ETH': token['balance']} # only ETH balance

def get_transactions(address: str) -> list:
    with request.urlopen('https://api.zapper.fi/v1/transactions/%s?api_key=%s' % (address, zapper_api_key)) as url: # historical transactions from zapper
        data = json.loads(url.read().decode())
    return data

def revert_txns(transactions: list, balance: dict, end: int, txn_index: int) -> (int, dict): # returns new txn_index and balance
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
    while int(transactions[txn_index]['timeStamp']) >= end: # the balances would be the same if no transactions take place between the two times
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
                        else:
                            balance['ETH'] = 0
        txn_index += 1
        if txn_index >= len(transactions): return (txn_index, balance)
    return (txn_index, balance)

def get_historical_balance(address: str, transactions: list, start: int, end: int) -> dict:
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

    reverted = revert_txns(transactions, balance, end, 0) # revert transactions until we reach the end of our interval from the present
    txn_index, historical_balance[end] = reverted[0], reverted[1]

    for time in range(end - interval, start - interval - 1, -interval): # reverse chronological in variable interval
        historical_balance[time] = historical_balance[time + interval] # current balance is temporarily equivalent to prior balance
        reverted = revert_txns(transactions, historical_balance[time], time, txn_index)
        txn_index, historical_balance[time] = reverted[0], reverted[1]
    
    return historical_balance

def get_historical_balance_eth(address: str, transactions: list, start: int, end: int) -> dict:
    balance = get_curr_balance_eth(address)
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

    reverted = revert_txns_eth(transactions, balance, end, 0) # revert transactions until we reach the end of our interval from the present
    txn_index, historical_balance[end] = reverted[0], reverted[1]

    for time in range(end - interval, start - interval - 1, -interval): # reverse chronological in variable interval
        historical_balance[time] = historical_balance[time + interval].copy() # current balance is temporarily equivalent to prior balance
        reverted = revert_txns_eth(transactions, historical_balance[time], time, txn_index)
        txn_index, historical_balance[time] = reverted[0], reverted[1]
    
    return historical_balance

def get_historical_fiat_worth(historical_balance: dict, start: int, end: int) -> dict:
    pass

def get_daily_avg_pnl(hist_fiat_balance: dict, start: int, end: int) -> dict:
    pass

#print(get_tokens(address))

my_eth = 0

my_transactions = get_transactions(address)

#print(my_transactions)

print('found', len(my_transactions), 'transactions \n')


my_curr_balance = get_curr_balance_eth(address)

print(my_curr_balance)

hist_bal = get_historical_balance_eth(address, my_transactions, 1618384251, 1619618759)

for time in hist_bal:
    print(time, hist_bal[time])

#print(my_transactions)