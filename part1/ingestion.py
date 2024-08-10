import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

def check_api_status() -> bool:
    """
    Function that checks if the Coingecko API is working
    """

    API_STATUS_CHECK_URL = "https://api.coingecko.com/api/v3/ping?x_cg_demo_api_key=" + COINGECKO_API_KEY
    response = requests.get(API_STATUS_CHECK_URL)
    if response.status_code == 200:
        return True
    return False

def retrieve_hourly_data_over_week(coin_id: str) -> dict:
    """
    Function that returns an hourly interval of data as long as days is within 2-90 days
    """
    
    GET_HOURLY_PRICES_OVER_WEEK_URL = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
    response = requests.get(GET_HOURLY_PRICES_OVER_WEEK_URL)
    return response.json()

def retrieve_top_ten_coins() -> dict:
    """
    Function that returns the top 10 coins by market cap
    """

    GET_TOP_TEN_COINS_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    response = requests.get(GET_TOP_TEN_COINS_URL)
    return response.json()

def format_data() -> list:
    """
    Formats the date of prices
    """

    # Check if the API is working
    if not check_api_status():
        print("API is not working.")
        return []  # Return an empty list instead of None

    # Retrieve the top ten coins
    top_ten_coins = retrieve_top_ten_coins()

    # check if rate limited
    if len(top_ten_coins) < 10:
        print("Failed to retrieve top ten coins.")
        return []

    # Format the data
    formatted_data = []
    for coin in top_ten_coins:
        try:
            coin_data = retrieve_hourly_data_over_week(coin['id'])
            updated_prices = []

            # turn each timestamp into a readable date
            for price_entry in coin_data['prices']:
                if isinstance(price_entry, list) and len(price_entry) == 2:
                    timestamp = price_entry[0] / 1000  # Convert from milliseconds to seconds
                    price = price_entry[1]
                    readable_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    updated_prices.append([readable_date, price])
            formatted_data.append({
                'id': coin['id'],
                'prices': updated_prices
            })
        except KeyError as e:
            print(f"Error: 'prices' key not found in data for coin {coin['id']} as a result of rate limit")
            continue # after we hit the rate limit, we skip the coin
    
    #print(formatted_data)
    if not formatted_data:
        print("Coin data is not in expected format.")
        return []  # Return an empty list instead of None

    return formatted_data