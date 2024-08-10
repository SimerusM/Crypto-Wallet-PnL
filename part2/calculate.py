import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
from tabulate import tabulate

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from part1 import retrieve_data

load_dotenv()

def get_wallet_balances(wallet_address: str) -> dict:
    """
    Function to retrieve the balances of tokens in a given wallet address.

    Parameter:
        wallet_address (str): The address of the wallet

    Returns:
        dict: Contains all the meta data associated with the particular wallet
    """
    API_URL = "https://api.allium.so/api/v1/explorer/queries/UWHFUe3BPTFpd7EDVIiI/run"
    API_KEY = os.getenv('ALLIUM_API_KEY')
    
    response = requests.post(
        API_URL, 
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': API_KEY
        }, 
        json = {
            "address": wallet_address
        }
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve wallet balances: {response.status_code}")
        return {}
    

def format_date(date_str: str) -> str:
    """
    Function to format the dates

    Parameter:
        date_str (str): A string of a date that looks like this: 2024-08-09 01:17:39

    Returns:
        str: A beautified date string that looks like this: Aug 9, 01:00
    """

    # Parse the input date string into a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # Round down the time to the nearest hour
    date_obj = date_obj.replace(minute=0, second=0, microsecond=0)

    # Format the datetime object into the desired string format
    formatted_date = date_obj.strftime("%b %-d, %H:%M")
    
    return formatted_date


def find_token_balances(wallet_data: list) -> dict[tuple]:
    """
    Function to find distinct tokens and their total balances

    Parameter:
        wallet_data (list): A list of the elements in the "data" key of the wallet

    Returns:
        dict: A dictionary contaning tuples of distinct token ids and their total espective balance in the wallet
    """
    
    token_balances = {}

    # for each entry data containing a balance and token, find all distinct tokens and find their total balance
    for entry in wallet_data:
        token_id = entry['token_id']
        balance = entry['balance']
        
        if token_id in token_balances:
            token_balances[token_id] += balance
        else:
            token_balances[token_id] = balance

    # token_balances containing the total balance for each token_id
    return [(token_id, balance) for token_id, balance in token_balances.items()]

def calculate_overall_pnl(portfolio_data: list[dict]) -> list[list]:
    """
    Function that calculates the overall PnL of a given wallet (sum the PnLs of each token)
    The PnLs are calculated at each corresponding hour
    
    Parameter:
        portfolio_data (list): A list of dictionaries where each dictionary contains token id and its hourly PnL data.

    Returns:
        list: A list containing the overall PnL at each hour.
    """
    
    # Initialize a list to store the overall PnL at each hour
    overall_pnl_list = []

    # Assuming all tokens have the same number of hourly data points
    for i in range(len(portfolio_data[0]['hourly_data'])):
        date = portfolio_data[0]['hourly_data'][i][0]
        total_pnl = sum(token_data['hourly_data'][i][1] for token_data in portfolio_data)
        
        overall_pnl_list.append([date, total_pnl])

    return overall_pnl_list


def calculate_pnl(wallet_address: str) -> list[list]:
    """
    Function that calculates profit and loss of wallet tokens over the past week

    Parameter:
        wallet_address (str): The address of the particular wallet you want to scrape data from

    Returns:
        list: A list containing the overall PnL at each hour.
    """

    # Get general wallet data
    wallet_general_info = get_wallet_balances(wallet_address)

    # Sort wallet data by block timestamp, format: [{token_address, balance, timestamp, token_id}, ....]
    wallet_data = sorted(wallet_general_info["data"], key=lambda x: x["block_timestamp"])

    # token_balances containing the total balance for each token_id, format: (token_id: str, total balance: float)
    distinct_tokens_with_balances = find_token_balances(wallet_data)

    # Store the processed hourly data with hourly PnLs of each individual token
    # format: [{distinct token id: str, hourly_data: list[list]}]
    individual_token_processed_data = []

    # loop through the distinct tokens the wallet contains
    for token_id, balance in distinct_tokens_with_balances:
        value = 0 # variable to hold current hourly value
        profit_n_loss = 0 # variable to hold current hourly pnl
        coin_data_dict = {"id": token_id} 
        hourly_pnl = []

        # Get the token price data over the last week
        weekly_token_data = retrieve_data.retrieve_specific_data(token_id)
        for num, hourly_data in enumerate(weekly_token_data):
            date, price = format_date(hourly_data[0]), hourly_data[1] * balance

            # Account for the very first value
            if num == 0:
                value = price
            else:
                profit_n_loss += price - value
                value = price
    
            hourly_pnl.append([date, round(profit_n_loss)])
        
        coin_data_dict["hourly_data"] = hourly_pnl
        individual_token_processed_data .append(coin_data_dict)
    
    return calculate_overall_pnl(individual_token_processed_data)

def main():
    wallet_address = "0x26a016De7Db2A9e449Fe5b6D13190558d6bBCd5F" # place your wallet address here
    pnl = calculate_pnl(wallet_address)
    
    print(tabulate(pnl, headers=["Date", "PnL"], tablefmt="pretty"))


main()
