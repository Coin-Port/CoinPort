from functions import *
import time

address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9'

start = 1611371447
end = int(time.time())

my_txs = get_transactions_ethscan(address)

print('im here')

with open('get_txn_ethscan_test.json', 'w') as f:
    f.write(str(my_txs))
    f.close()

print('and now im here')

hist_bal = get_historical_balance(address, my_txs, start, end)

print('but not before im there')

readable_hist_bal = human_time_hist_bal(hist_bal)

print('then im here')

with open('historical_balance.json', 'w') as f:
    f.write(str(hist_bal))
    f.close()