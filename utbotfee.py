import vectorbt as vbt
import pandas as pd
import numpy as np
import talib
import datetime as dt
import json
import requests

URL = 'https://api.binance.com/api/v3/klines'

intervals_to_secs = {
    '1m':60,
    '3m':180,
    '5m':300,
    '15m':900,
    '30m':1800,
    '1h':3600,
    '2h':7200,
    '4h':14400,
    '6h':21600,
    '8h':28800,
    '12h':43200,
    '1d':86400,
    '3d':259200,
    '1w':604800,
    '1M':2592000
}

def download_kline_data(start: dt.datetime, end:dt.datetime ,ticker:str, interval:str)-> pd.DataFrame:
    start = int(start.timestamp()*1000)
    end = int(end.timestamp()*1000)
    full_data = pd.DataFrame()

    while start < end:
        par = {'symbol': ticker, 'interval': interval, 'startTime': str(start), 'endTime': str(end), 'limit':1000}
        data = pd.DataFrame(json.loads(requests.get(URL, params= par).text))

        data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.iloc[:,0]]
        data=data.astype(float)
        full_data = pd.concat([full_data,data])

        start+=intervals_to_secs[interval]*1000*1000

    full_data.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume','Close_time', 'Qav', 'Num_trades','Taker_base_vol', 'Taker_quote_vol', 'Ignore']

    return full_data

SENSITIVITY = 1
ATR_PERIOD = 10

TICKER = "BTCUSDT"
INTERVAL = "1d"

START = dt.datetime(2017,8,17)
END   = dt.datetime.now()

pd_data = download_kline_data(START, END, TICKER, INTERVAL)

pd_data["xATR"] = talib.ATR(pd_data["High"], pd_data["Low"], pd_data["Close"], timeperiod=ATR_PERIOD)
pd_data["nLoss"] = SENSITIVITY * pd_data["xATR"]

pd_data = pd_data.dropna()
pd_data = pd_data.reset_index()

def xATRTrailingStop_func(close, prev_close, prev_atr, nloss):
    if close > prev_atr and prev_close > prev_atr:
        return max(prev_atr, close - nloss)
    elif close < prev_atr and prev_close < prev_atr:
        return min(prev_atr, close + nloss)
    elif close > prev_atr:
        return close - nloss
    else:
        return close + nloss

pd_data["ATRTrailingStop"] = [0.0] + [np.nan for i in range(len(pd_data) - 1)]

for i in range(1, len(pd_data)):
    pd_data.loc[i, "ATRTrailingStop"] = xATRTrailingStop_func(
        pd_data.loc[i, "Close"],
        pd_data.loc[i - 1, "Close"],
        pd_data.loc[i - 1, "ATRTrailingStop"],
        pd_data.loc[i, "nLoss"],
    )

ema = vbt.MA.run(pd_data["Close"], 1, short_name='EMA', ewm=True)

pd_data["Above"] = ema.ma_crossed_above(pd_data["ATRTrailingStop"])
pd_data["Below"] = ema.ma_crossed_below(pd_data["ATRTrailingStop"])

pd_data["Buy"] = (pd_data["Close"] > pd_data["ATRTrailingStop"]) & (pd_data["Above"]==True)
pd_data["Sell"] = (pd_data["Close"] < pd_data["ATRTrailingStop"]) & (pd_data["Below"]==True)

fee = 0.0002

pf = vbt.Portfolio.from_signals(
    pd_data["Close"],
    entries=pd_data["Buy"],
    short_entries=pd_data["Sell"],
    upon_opposite_entry='ReverseReduce',
    freq="d",
    fees=fee
)

pf.stats()




"""
Start                                                  0
End                                                 2546
Period                                2547 days 00:00:00
Start Value                                        100.0
End Value                                     243.713443
Total Return [%]                              143.713443
Benchmark Return [%]                         1255.739314
Max Gross Exposure [%]                             100.0
Total Fees Paid                                30.367347
Max Drawdown [%]                               61.712994
Max Drawdown Duration                  919 days 00:00:00
Total Trades                                         277
Total Closed Trades                                  276
Total Open Trades                                      1
Open Trade PnL                                 -3.884591
Win Rate [%]                                   35.144928
Best Trade [%]                                126.598643
Worst Trade [%]                               -21.224869
Avg Winning Trade [%]                          13.453097
Avg Losing Trade [%]                           -5.539807
Avg Winning Trade Duration    15 days 03:27:50.103092783
Avg Losing Trade Duration      5 days 23:27:49.273743016
Profit Factor                                   1.052693
Expectancy                                      0.534775
Sharpe Ratio                                    0.520762
Calmar Ratio                                    0.220645
Omega Ratio                                     1.084634
Sortino Ratio                                   0.811038
dtype: object
"""
