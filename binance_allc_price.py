import requests


BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"

def get_all_ticker_prices():
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        ticker_data = response.json()
        return ticker_data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    all_ticker_prices = get_all_ticker_prices()
    
    if all_ticker_prices:
        for ticker in all_ticker_prices:
            symbol = ticker['symbol']
            price = ticker['price']
            print(f"Symbol: {symbol}, Price: {price}")
