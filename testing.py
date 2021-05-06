from functions import *
import time

address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9'

my_txs = get_transactions(address)

end = int(time.time())
start = end - (3600 * 24 * 3)

print('im here')

print(get_price_history_interval('aDai', start, end, 'usd'))

with open('get_txn_ethscan_test.json', 'w') as f:
    f.write(str(my_txs))
    f.close()

print('and now im here')

hist_bal = get_historical_balance(address, my_txs, start, end)

print('but not before im there')

readable_hist_bal = human_time_hist_bal(hist_bal)

print('then im here')

with open('historical_balance.json', 'w') as f:
    f.write(str(readable_hist_bal))
    f.close()
