import requests
import pandas as pd


symbol = 'BTCUSDT'

def get_funding_fee_history(symbol, limit=10):
    url = 'https://fapi.binance.com/fapi/v1/fundingRate'
    params = {
        'symbol': symbol,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        funding_fee_history = response.json()
        
        df = pd.DataFrame(funding_fee_history)
        df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching funding fee history: {e}")
        return None

funding_fee_history = get_funding_fee_history(symbol, limit=10)

if funding_fee_history is not None and not funding_fee_history.empty:
    print(funding_fee_history)
else:
    print("No data available.")
