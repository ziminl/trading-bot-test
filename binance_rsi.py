# pip install python-binance

import pandas as pd
import datetime as dt
from binance.client import Client
import time
import numpy
import requests

# bollingerband using 1 minute data

#Buy if the price is above the upper band

#Sell if the price is below the lower band


while True:
    api_key='api_key'
    api_secret='api_secret'

    client = Client(api_key=api_key, api_secret=api_secret)
    # ticker of product
    symbo1_trade = 'XRPBUSD' #,'btcusdt'

    # order quantity (more than 10 USDT)
    orderquantity = 35

    # bollingerband length and width
    length = 20
    width = 2


    def bollingerband(symbol, width, intervalunit, length):

        if intervalunit == '1T':
            start_str = '100 minutes ago UTC'
            interval_data = '1m'

            D = pd.DataFrame(
                client.get_historical_klines(symbol=symbol, start_str=start_str, interval=interval_data))
            D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                         'taker_base_vol', 'taker_quote_vol', 'is_best_match']
            D['open_date_time'] = [dt.datetime.fromtimestamp(x / 1000) for x in D.open_time]
            D['symbol'] = symbol
            D = D[['symbol', 'open_date_time', 'open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol',
                   'taker_quote_vol']]

        df = D.set_index("open_date_time")

        df['close'] = df['close'].astype(float)

        df = df['close']

        df1 = df.resample(intervalunit).agg({

            "close": "last"
        })

        unit = width

        band1 = unit * numpy.std(df1['close'][len(df1) - length:len(df1)])

        bb_center = numpy.mean(df1['close'][len(df1) - length:len(df1)])

        band_high = bb_center + band1

        band_low = bb_center - band1

        return band_high, bb_center, band_low,


    bb_1m = bollingerband(symbo1_trade, width, '1T', length)

#Copyright by Bitone Great    www.bitonegreat.com

    print('1 minute upper center lower: ', bb_1m)

    marketprice = 'https://api.binance.com/api/v1/ticker/24hr?symbol=' + symbo1_trade
    res = requests.get(marketprice)
    data = res.json()
    lastprice = float(data['lastPrice'])

    print(lastprice)

    

    try:
        if lastprice > bb_1m[0]:
            print('sell')
            client.order_market_sell(symbol=symbo1_trade, quantity=orderquantity)
            break
            #the loop stops if the order is made
    except:
        pass

    try:
        if lastprice < bb_1m[2]:
            print('buy')
            client.order_market_buy(symbol=symbo1_trade, quantity=orderquantity)
            break
            #the loop stops if the order is made        
    except:
        pass

    time.sleep(1)
