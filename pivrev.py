import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time  

def check_trend_line(support: bool, pivot: int, slope: float, y: np.array):

    intercept = -slope * pivot + y[pivot]
    line_vals = slope * np.arange(len(y)) + intercept
     
    diffs = line_vals - y
    
    if support and diffs.max() > 1e-5:
        return -1.0
    elif not support and diffs.min() < -1e-5:
        return -1.0

    err = (diffs ** 2.0).sum()
    return err;


def optimize_slope(support: bool, pivot:int , init_slope: float, y: np.array):
    
    slope_unit = (y.max() - y.min()) / len(y) 
    
    opt_step = 1.0
    min_step = 0.0001
    curr_step = opt_step 
    
    best_slope = init_slope
    best_err = check_trend_line(support, pivot, init_slope, y)
    assert(best_err >= 0.0) # Shouldn't ever fail with initial slope

    get_derivative = True
    derivative = None
    while curr_step > min_step:

        if get_derivative:

            slope_change = best_slope + slope_unit * min_step
            test_err = check_trend_line(support, pivot, slope_change, y)
            derivative = test_err - best_err;
            

            if test_err < 0.0:
                slope_change = best_slope - slope_unit * min_step
                test_err = check_trend_line(support, pivot, slope_change, y)
                derivative = best_err - test_err

            if test_err < 0.0: 
                raise Exception("derivative failed. ")

            get_derivative = False

        if derivative > 0.0: 
            test_slope = best_slope - slope_unit * curr_step
        else: # increasing slope decreased error
            test_slope = best_slope + slope_unit * curr_step
        

        test_err = check_trend_line(support, pivot, test_slope, y)
        if test_err < 0 or test_err >= best_err: 
            curr_step *= 0.5 #stepsivze
        else: # test error
            best_err = test_err 
            best_slope = test_slope
            get_derivative = True # Recompute derivative
    

    return (best_slope, -best_slope * pivot + y[pivot])


def fit_trendlines_high_low(high: np.array, low: np.array, close: np.array):
    coefs = np.polyfit(x, close, 1)
    line_points = coefs[0] * x + coefs[1]
    upper_pivot = (high - line_points).argmax() 
    lower_pivot = (low - line_points).argmin() 
    
    support_coefs = optimize_slope(True, lower_pivot, coefs[0], low)
    resist_coefs = optimize_slope(False, upper_pivot, coefs[0], high)

    return (support_coefs, resist_coefs)

exchange = ccxt.binance()
symbol = 'BTC/USDT'

data = pd.DataFrame(columns=['high', 'low', 'close'])

while True:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=30)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        aggregated_data = df.tail(30)
        
        high_prices = aggregated_data['high'].values
        low_prices = aggregated_data['low'].values
        close_prices = aggregated_data['close'].values
        
        support_coefs, resist_coefs = fit_trendlines_high_low(high_prices, low_prices, close_prices)
        
        print("Fetched OHLCV data:", aggregated_data)

        print("Support Coefficients:", support_coefs)
        print("Resistance Coefficients:", resist_coefs)

        time.sleep(60)
        
    except Exception as e:
        print("Error occurred:", e)
        time.sleep(10)
