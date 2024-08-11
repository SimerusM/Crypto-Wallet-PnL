# Part 1

### Setup
To ensure that your environment is isolated and consistent, set up a virtual environment:
`python -m venv venv`.
Activate it using `source venv/bin/activate` on macOS/Linux or `venv\Scripts\activate` on Windows. 

Install all the necessary dependencies using the requirements.txt file: `pip install -r requirements.txt`.

Copy the `example.env` file into an actual `.env` file using `cp example.env .env`, and then copy and paste the respective keys/URIs into its place.

**MongoDB**

To get the MongoDB URI, create a "New Project" from your MongoDB organization home page after navigating to "Projects". In this new project create a cluster, follow the instructions and make sure to set up a driver. Make sure to copy and paste the conneciton string of the driver that looks like this: `mongodb+srv://<user>:<password>@cluster0.633pc.mongodb.net/?retryWrites=true&w=majority&appName=<cluster name>`, where you replace the placeholders with your own information.

**CoinGecko**

Go to the CoinGecko dashboard, click on your profile and go to "Developer's Dashboard". Once you're there, either create or copy and paste an API key.

**Allium Key**

Provied in the assignment: 5jwLBV9oVitGnSfkGl6rp5hhJzDbBvoKa-4KllVq5L4CoxfIv_-AT8jrNblF16YhXBKiZkdqzG16ZZSZW4m8CA

Once you have all the proper keys in the `.env`, now we can start running each of the scripts. The main ones for the part 1 functionality are `ingestion.py` and `store_data.py` (ingestion gets called in store_data). To start the ingestion process of getting the top 10 coins by market cap and getting the last 7 days worth of hourly data, enter into the `part1` folder with `cd part1` from the root directory and run the command `python store_data.py`. This will automatically call the `ingestion.py` script for the data ingestion, and then it stores this data that we collected from the ingestion script onto MongoDB.

Note that the ingestion script uses the free CoinGecko URL for retrieval. To avoid rate limiting and if you do have a premium account add `&x_cg_pro_api_key={COINGECKO_API_KEY}` to the end of both `GET_HOURLY_PRICES_OVER_WEEK_URL` and `GET_TOP_TEN_COINS_URL` located in `ingestion.py` in the functions `retrieve_hourly_data_over_week(coin_id: str)` and `retrieve_top_ten_coins()` respectively like so:

`GET_HOURLY_PRICES_OVER_WEEK_URL = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7&x_cg_pro_api_key={COINGECKO_API_KEY}"`
`GET_TOP_TEN_COINS_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&x_cg_pro_api_key={COINGECKO_API_KEY}"`


# Part 2

Make sure you're in the part2 folder by cd part2 from the root. All you need to do is run python calculate.py to see a tabular result of the PnL of the portfolio. Ensure that you run the scripts in part1 to make sure you have data in the MongoDB database.

**ASSUMPTIONS MADE:**

Initial PnL Value: The initial PnL value is assumed to be 0. This means that at the start of the calculation, the portfolio's profit and loss are considered neutral.

Wallet Token Data: It is assumed that all tokens in the wallet were purchased before the last week. This assumption simplifies the calculation by ensuring that the entire balance of each token is present for the full duration of the PnL calculation period.

Aggregation of Token Balances: Instead of determining the price of each token at the specific time of purchase, the total balance of each token in the wallet is aggregated. This aggregated balance is used from the very first hour of the week under consideration. The PnL calculation then builds on this aggregated balance as it tracks the hourly changes in token prices. We have a PnL aggregation of each distinct coin in the portfolio, and then at the end we calculate the overall PnL of the portfolio by summing the PnLs of each token at each respective hour.

Handling Multiple Tokens: Although the provided wallet mainly contains information on Ethereum purchases, the calculate.py script is designed to handle multiple tokens in the wallet, calculating the PnL for each token and then combining them to give an overall portfolio PnL.

