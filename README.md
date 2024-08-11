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

<br/>

### Ingestion

Once you have all the proper keys in the `.env`, now we can start running each of the scripts. The main ones for the part 1 functionality are `ingestion.py` and `store_data.py` (ingestion gets called in store_data). To start the ingestion process of getting the top 10 coins by market cap and getting the last 7 days worth of hourly data, enter into the `part1` folder with `cd part1` from the root directory and run the command `python store_data.py`. This will automatically call the `ingestion.py` script for the data ingestion, and then it stores this data that we collected from the ingestion script onto MongoDB.

Note that the ingestion script uses the free CoinGecko URL for retrieval. To avoid rate limiting and if you do have a premium account add `&x_cg_pro_api_key={COINGECKO_API_KEY}` to the end of both `GET_HOURLY_PRICES_OVER_WEEK_URL` and `GET_TOP_TEN_COINS_URL` located in `ingestion.py` in the functions `retrieve_hourly_data_over_week(coin_id: str)` and `retrieve_top_ten_coins()` respectively like so:

`GET_HOURLY_PRICES_OVER_WEEK_URL = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7&x_cg_pro_api_key={COINGECKO_API_KEY}"`

`GET_TOP_TEN_COINS_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&x_cg_pro_api_key={COINGECKO_API_KEY}"`

Once you run `store_data.py` you've successfully ingested the data and added it to the persistent MongoDB storage. There is also a file called `retrieve_data.py` which provides a function called `retrieve_data()` that acts as a check to see if everything got successfully added to the database, to run this function, add `retrieve_data()` to the bottom of the file and run the file with `python retrieve_data.py`.

# Part 2

Make sure you're in the `part2` folder by running `cd part2` from the root directory. All you need to do is run `python calculate.py` to see a tabular result of the PnL of the portfolio. Ensure that you run the scripts in Part 1 to make sure you have data in the MongoDB database.

**ASSUMPTIONS MADE:**

Initial PnL Value: The initial PnL value is assumed to be 0. This means that at the start of the calculation, the portfolio's profit and loss are considered neutral.

Wallet Token Data: It is assumed that all tokens in the wallet were purchased before the last week. This assumption simplifies the calculation by ensuring that the entire balance of each token is present for the full duration of the PnL calculation period.

Aggregation of Token Balances: Instead of determining the price of each token at the specific time of purchase, the total balance of each token in the wallet is aggregated. This aggregated balance is used from the very first hour of the week under consideration. The PnL calculation then builds on this aggregated balance as it tracks the hourly changes in token prices. We have a PnL aggregation of each distinct coin in the portfolio, and then at the end we calculate the overall PnL of the portfolio by summing the PnLs of each token at each respective hour.

Handling Multiple Tokens: Although the provided wallet mainly contains information on Ethereum purchases, the calculate.py script is designed to handle multiple tokens in the wallet, calculating the PnL for each token and then combining them to give an overall portfolio PnL.

Here's a sample result:

![Screenshot 2024-08-10 at 11 46 44 PM](https://github.com/user-attachments/assets/511d02ff-61d9-49cd-9e08-b8a389ebb2ee)


# Part 3

With an increase in tokens, granularity, and token timeframe, we're going to have to store more and more data (and process more for retrieval). A potential way to mitigate this is to horizontally scale our databases with database sharding wherein we distribute partioned data across multiple databases (e.g. coins in the top 1-1000 in terms of market cap go in database 1, top 1001-2000 go in database 2, etc...). With this, we can improve retrieval as queries can be executed in parallel to these shards to gather data quicker and it also prevents bottlenecks from occuring.

In each database shard, we can go further and batch process the data into smaller chunks (e.g. 100 tokens per batch in a db shard of 1000 tokens) and process multiple batches in parellel (assuming we have a multi core CPU).

If the exact value of individual data points isn't super important, rather, just the ability to get PnLs, we can consider aggregating the data and thus reduce the number of data points we have stored/need to process. Instead of storing every single fluctuation of data price in a 5 minute period, we can store the average of these fluctuations (and maybe other important data such as the high/low). Again, this would significantly help in terms of reducing the data volume but it depends on the use case of the system and if the individual data points themselves matter.

Say we need to calculate the PnL of a person with an ETH token from like 2018, loading all that data from 2018 up until now would be very resource intensive. To help with this process we can introduce incremental batching where we process data chunk by chunk as we go in sequential order. As we calculate the PnLs, we can cache these intermediate results so in the future we can just reuse these values which will significantly help in future scenarios where data needs to be reprocessed. 

As for the specific type of database, we can use something called a time-series database (e.g. InfluxDB) to further enhance the system/process. These databases are specifically designed to handle large volumes of time-indexed data and support fast queries over time ranges, making them ideal for storing and retrieving the historical price data needed for PnL calculations.

For database shards that potentially could get read heavy (e.g. the shard that stores the coins in the top 1-1000 like Bitcoin and Ethereum) we can implement read replicas of those shards to distribute the read loads. By introducing replication, we must also make sure to keep it persistent as well so we can choose between two different replication strategies. For scenarios where reads are going to be heavily conducted we can use the single-leader replication style where one node (leader) handles the writes and the replicas (followers) handle the reads. For write heavy scenarios a multi-leader replication style can be used where multiple nodes accept writes and changes get propogated to one another - we must be wary that with this option we must be able to deal with conflicts through means such as version vectors or last-write-wins.

Since we have replicas of popular database shards that experience heavy requests, we can introduce a load balancer (a type of reverse proxy) to handle distributing the traffic evenly using strategies like round robin. We can consider deploying this entire architecture in a Kubernetes cluster where it orchestrates the deployment and scaling of these systems (which can be containerized) by automatiaclly making new instances for an increase in demand.

For frequently accessed data (e.g. the top 1-1000 database shard data), we can consider adding a cache in front of the DB such as Redis to serve data faster and reduce load on the shard.

Speaking of caches and databases, this results in a lot of complexity to manage. If we want to stick to something easier to develop but very optimized, AWS offers something called MemoryDB which is essentially a super high performance cache that can also act as a database (GB to >100TB worth of storage). It is highly available as it has Multi-AZ (an exact copy of the database is also in another availability zone located in a different place, this is offererd by AWS) and a transaction log for recovery and durability. It is so scaleable that it can be used as a primary database.
The entire dataset for an application can be stored in memory and it supports >160 million requests per second with microsecond read and single-digit millisecond write latency. This is a great option if we want to use a cloud service to handle high scale PnL.








