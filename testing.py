from functions import *

address = input('address: ')

print(get_tokens(address))

my_transactions = get_transactions(address)
print(my_transactions[0])
'''
with open('0x7E379d280AC80BF9e5D5c30578e165e6c690acC9_test.txt', 'w') as f:
    f.write(str(my_transactions))
    f.close()
'''
print('found', len(my_transactions), 'transactions \n')

my_curr_balance = get_curr_balance(address)

print(my_curr_balance)
'''
hist_bal = get_historical_balance_eth(address, my_transactions, 1618384251, 1619618759)


for time in hist_bal:
    print(time, hist_bal[time])

print(len(hist_bal))

fiat_hist_bal = get_historical_fiat_worth_eth(hist_bal, 1618384251, 1619618759, 'USD')

pnl = get_pnl(fiat_hist_bal, 1618384251, 1619618759)

print(pnl)


for time in fiat_hist_bal:
    print(time, fiat_hist_bal[time])


print(my_transactions)''''''