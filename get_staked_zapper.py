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
                if token["symbol"] in symbol_lookup: 
                    symbol_lookup[[token["symbol"]].append(len(balances_sub)-1)
                symbol_lookup[token["symbol"] : [len(balances_sub)-1]] #dict of locations of occurence of a symbol
            balances_sub.sort(key = lambda k: k["symbol"])

    for indices in symbol_lookup:
        temp_balance = balances_sub[indices[0]]
        for index in indices[1:]:
            temp_balance["balance"] += balances_sub[index]["balance"]
            temp_balance["balanceUSD"] += balances_sub[index]["balanceUSD"]
        balances_main.append(temp_balance)

    return balances_main