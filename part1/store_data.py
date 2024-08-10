from pymongo import MongoClient
import ingestion
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)

db = client['crypto_data']
collection = db['crypto_prices']

def store_data_in_mongodb() -> None:
    """
    Function that calls the ingestion script and stores the data in MongoDB
    """

    # get the data
    data_list = ingestion.format_data()

    if not data_list:
        return

    # Insert each JSON object into MongoDB
    for data in data_list:
        # Insert the JSON object into the collection
        collection.insert_one(data)
        print(f"Inserted data for {data['id']} into MongoDB.")

store_data_in_mongodb()
