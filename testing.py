from functions import *
import time
from cryptoaddress import EthereumAddress
import json
from urllib import request

address = '0xEf40c39851b6669dad6f73dE7578760201968908'
address2 = '0x7e379d280ac80bf9e5d5c30578e165e6c690acc9'

data = [0,1,2,3,4,5,6,7,8,9]

print(data[:6])


exit()

'''staked = get_staked_zapper(address2)
pool = get_pool_balance_zapper(address2)

with open('pool.json', 'w') as f:
    f.write(str(pool))
    f.close()

with open('staked.json', 'w') as f:
    f.write(str(staked))
    f.close()

exit()'''

#print(get_staked_zapper(address2))
#print(get_pool_balance_zapper(address2))
#print("\n\n\n\n\n")
address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9'
#address = '0x7B88DF8AF7a283e3dc84A7Fd97Fde19cAbb90eD4'

my_txs = get_transactions(address)

end = int(time.time())
start = end - 1000000

print('im here')

#print(get_price_history_interval('link', start, end, 'usd'))

with open('get_txn_ethscan_test.json', 'w') as f:
    f.write(str(my_txs))
    f.close()

print('and now im here')

balance = get_curr_balance(address)

hist_bal = get_historical_balance(balance, address, my_txs, start, end)

print('but not before im there')

readable_hist_bal = human_time_hist_bal(hist_bal)

print('then im here')

with open('historical_balance.json', 'w') as f:
    f.write(str(hist_bal))
    f.close()

min_time = hist_bal.keys()[-1]
max_time = hist_bal.keys()[0]

print(min_time, max_time)
