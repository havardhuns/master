import json
import os
from time import sleep
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db["transactions-block-500"]

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)

transactions = collection.find({})
for transaction in transactions:
    entities = []
    inputs = transaction["inputs"]
    for inp in inputs:
        entity = addresses_api.get_address_entity('btc', inp["address"][0])["entity"]
        if entity not in entities:
            entities.append(entity)
    print(entities)