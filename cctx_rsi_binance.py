import ccxt
import pandas as pd
import time

def rsi_calc(ohlc: pd.DataFrame, period: int = 14):
    ohlc = ohlc[4].astype(float)
    delta = ohlc.diff()
    gains, declines = delta.copy(), delta.copy()
    gains[gains < 0] = 0
    declines[declines > 0] = 0

    _gain = gains.ewm(com=(period-1), min_periods=period).mean()
    _loss = declines.abs().ewm(com=(period-1), min_periods=period).mean()

    RS = _gain / _loss
    return pd.Series(100-(100/(1+RS)), name="RSI")

def rsi_binance(itv='1h', simbol='BTC/USDT'):
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe=itv, limit=200)
    df = pd.DataFrame(ohlcv)
    rsi = rsi_calc(df,14).iloc[-1]
    return rsi

while True:
    print("15m " + str(rsi_binance(itv='15m')))
    print("1h " + str(rsi_binance(itv='1h')))
    print("4h " + str(rsi_binance(itv='4h')))
    time.sleep(1)
