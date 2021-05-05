supported_protocols = { 
    "binance-smart-chain": [
      "autofarm",
      "ellipsis",
      "harvest",
      "tokens",
      "venus",
      "pancakeswap"
    ],
    "ethereum": [
      "alpha",
      "alchemix",
      "aave(v2)",
      "aave-amm",
      "aave",
      "b-protocol",
      "badger",
      "balancer",
      "bancor",
      "barnbridge",
      "bitcoin",
      "compound",
      "cover",
      "cream",
      "curve",
      "defisaver",
      "derivadex",
      "dforce",
      "dhedge",
      "dodo",
      "dsd",
      "dydx",
      "esd",
      "futureswap",
      "harvest",
      "hegic",
      "idle",
      "keeper-dao",
      "liquity",
      "linkswap",
      "loopring",
      "maker",
      "mooniswap",
      "1inch",
      "nft",
      "other",
      "pickle",
      "pooltogether",
      "rari",
      "realt",
      "reflexer",
      "saddle",
      "sfinance",
      "shell",
      "smoothy",
      "snowswap",
      "sushiswap",
      "swerve",
      "synthetix",
      "tokensets",
      "tokens",
      "uniswap(v2)",
      "uniswap",
      "unit",
      "value",
      "vesper",
      "xsigma",
      "yearn"
    ],
    "optimism": [
        "synthetix"
    ],
    "polygon": [
        "tokens",
        'quickswap',
        'aave-v2',
        'curve',
        'pooltogether'
    ]
}

from json import loads, dump
from urllib import request

coingecko_coin_list = {coin['symbol']: {i:coin[i] for i in ['id', 'name', 'platforms']} for coin in loads(request.urlopen('https://api.coingecko.com/api/v3/coins/list?include_platform=true').read().decode())}

with open('coin_list.json', 'w') as f:
   dump(coingecko_coin_list, f)