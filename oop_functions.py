import json
from urllib import request
from time import strptime, struct_time, time, mktime
from coin_list import coingecko_coin_list
from coin_list import supported_protocols as zapper_supported_protocols
from datetime import datetime
from decimal import Decimal
import cryptoaddress
from dataclasses import dataclass

#address = '0x7E379d280AC80BF9e5D5c30578e165e6c690acC9' # my address that i was testing
#address = '0x145c692ea0B7D8dD26F0eD6230b2fC6c44EffdA1' # random address from the list that JC sent
zapper_api_key = '96e0cc51-a62e-42ca-acee-910ea7d2a241' # public use API key
ethscan_api_key = 'JBD58KU8MHIJ374AX3J1ICHX4F64YAKMAD'
covalent_api_key = 'ckey_6c3f3233e25f4ad1bfe6cfc2403'

# modifications to functions.py using OOP

class address:
    def __init__(self, name, address, total_bal, network_bals, liquidity_pools, staked, yield_farming):
        self.name = name # nickname for address
        self.address = address # ethereum address
        self.total_bals = total_bal # total balances (sum of other balances)
        self.network_bals = network_bals # balances on various networks, e.g. Ethereum, BSC, Polygon, etc..
        self.liquidity_pools = liquidity_pools # balances on liquidity pools
        self.staked = staked # balances staked, e.g. SushiSwap? (kind of a weird one since I would consider this an LP but I'm just going off of Zapper) could change, since I'm probably gonna go with Covalent
        self.yield_farming = yield_farming # balances from yield farming

    
    