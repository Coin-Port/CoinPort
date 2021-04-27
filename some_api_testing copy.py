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

def get_transactions(address): # historical transactions
    with request.urlopen('https://api.zapper.fi/v1/transactions/%s?api_key=%s' % (address, zapper_api_key)) as url: # historical transactions from zapper
        zapper_data = json.loads(url.read().decode())[::-1] # originally reverse chronological
    print(zapper_data)
    with request.urlopen('https://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s' % (address, ethscan_api_key)) as url: # historical transactions from etherscan
        ethscan_data = json.loads(url.read().decode()) # already chronological
        if ethscan_data['status'] != '1':
            print('error fetching data')
            return False
        ethscan_data = ethscan_data['result']
    # why am i using both?
    # zapper has easy to parse data but doesn't know if a transaction went through or not
    # etherscan tells me if a transaction went through but sucks to parse
    # they also have transactions that the other doesn't have for whatever reason, it's really annoying so I'm going to deal with that here..

    txn_hashes = set() # keys will be hashes, two transactions from a user can happen at the same time so timestamp isn't an option
    # i'll insert hashes into chronological order, then go in that order to make an empty dictionary as dictionaries maintain insertion order
    # and then keep track of chronlogy with a tuple of hash and timestamp
    # using a set so there's no repeats

    for txn in zapper_data:
        txn_hashes.add((int(txn['timeStamp']), txn['hash']))

    for txn in ethscan_data:
        txn_hashes.add((int(txn['timeStamp']), txn['hash']))

    txn_hashes = [i[1] for i in sorted(list(txn_hashes))] # get only hashes, sorts by the timestamps since they're index 0, so they're in chronological order
    
    data = {}

    for hash in txn_hashes:
        data[hash] = {}
        data[hash]['onEthscan'] = False
        data[hash]['isError'] = 0 # assume transaction went through

    
    for txn in ethscan_data:
        data[txn['hash']]['direction'] = 'outgoing' if txn['from'].lower() == address.lower() else 'incoming'
        data[txn['hash']]['symbol'] = 'ETH'
        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
        data[txn['hash']]['gas'] = float(txn['gasPrice']) / 1000000000000000000 * float(txn['gasUsed']) # 1 billion * 1 billion because wei -> gwei -> eth
        data[txn['hash']]['onZapper'] = False # don't know if i'm gonna use this but keeping it just in case
        data[txn['hash']]['onEthscan'] = True
        data[txn['hash']]['isError'] = int(txn['isError'])

    for txn in zapper_data:
        data[txn['hash']]['direction'] = txn['direction']
        data[txn['hash']]['symbol'] = txn['symbol']
        data[txn['hash']]['timeStamp'] = int(txn['timeStamp'])
        data[txn['hash']]['amount'] = float(txn['amount'])
        data[txn['hash']]['subTransactions'] = txn['subTransactions']
        data[txn['hash']]['gas'] = float(txn['gas'])
        data[txn['hash']]['onZapper'] = True

    return data

def get_balance(transactions: dict, time: int) -> dict:
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

#print(get_tokens(address))

my_eth = 0

my_transactions = get_transactions(address)

#print(my_transactions)

print('found', len(my_transactions), 'transactions \n')

#print(my_transactions)

my_balance = get_balance(my_transactions, time.time())

#for i in my_transactions: print(i)
print('')
print(my_balance)