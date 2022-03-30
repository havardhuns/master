import json
import os
from time import sleep
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api
from tqdm import tqdm
import names

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
transactions_collection = db["transactions"]
addresses_collection = db["interesting-addresses"]

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
blocks_api = blocks_api.BlocksApi(api_client)
bulk_call_api = bulk_api.BulkApi(api_client)

currency = "btc"
block_height = 600000


block_transactions = blocks_api.list_block_txs(currency, block_height)
print(len(block_transactions))
addresses = []

# get first input addresses from each transaction
for transaction in block_transactions[1::10]:
    address = transaction.inputs.value[0].address[0]
    if address not in addresses:
        addresses.append(address)

data = [{"_id": address, "name": names.get_full_name(), "known_addresses": [address], "aggregated_inputs": [], "aggregated_ouputs": []}
        for address in addresses]
addresses_collection.insert_many(data)
