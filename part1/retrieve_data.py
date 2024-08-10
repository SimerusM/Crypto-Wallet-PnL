from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI') 

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)

# Select the database and collection
db = client['crypto_data']
collection = db['crypto_prices']

def retrieve_data() -> dict:
    """
    Function that retrieves all MongoDB stored data and prints it for testing
    """

    # Retrieve all documents in the collection
    all_documents = collection.find()

    for document in all_documents:
        # Print the document in a readable format
        print(f"ID: {document['id']}")
        print("Prices:")
        for price_entry in document['prices']:
            date_time = price_entry[0]
            price = price_entry[1]
            print(f"  Date: {date_time}, Price: {price}")
        
        print("\n")  # Add a new line for separation between documents
    
    return all_documents

def retrieve_specific_data(coin: str) -> list:
    """
    Function that retrieves the prices of a specific coin from MongoDB stored data
    """

    # Retrieve all documents in the collection
    specific_documents = collection.find({"id": coin})
    prices = []

    for document in specific_documents:
        for price_entry in document['prices']:
            prices.append(price_entry)
    
    return prices
