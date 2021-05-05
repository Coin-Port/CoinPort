from functions import *
import time

address = '0xEf40c39851b6669dad6f73dE7578760201968908'

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
