#to compare spot vs future

import ccxt
from datetime import datetime
import pandas as pd

api_key = 'your_api_key'
api_secret = 'your_api_secret'

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future'
    }
})

def get_funding_fee_history(symbol, limit=10):
    try:
        funding_fee_history = exchange.fapiPrivate_get_fundingrate({
            'symbol': symbol,
            'limit': limit
        })
        
        df = pd.DataFrame(funding_fee_history)
        df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
        return df
    
    except Exception as e:
        print(f"Error fetching funding fee history: {e}")
        return None

symbol = 'BTCUSDT'
funding_fee_history = get_funding_fee_history(symbol, limit=10)

if funding_fee_history is not None and not funding_fee_history.empty:
    print(funding_fee_history)
else:
    print("No data available.")
