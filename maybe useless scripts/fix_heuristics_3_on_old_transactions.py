import os
from time import sleep
import graphsense
from numpy import block
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, bulk_api, txs_api, entities_api
from tqdm import tqdm
from aggregate_outputs import value_has_more_than_four_decimals

load_dotenv('.env')



api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)
txs_api = txs_api.TxsApi(api_client)
entities_api = entities_api.EntitiesApi(api_client)

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
aggregated_transactions_collection = db["aggregated-transactions"]
changed = 0
aggregated_transactions = aggregated_transactions_collection.find({"aggregated_outputs.heuristics.3": True})
for aggregated_transaction in aggregated_transactions:
    otc_output_value = aggregated_transaction["aggregated_outputs"]["otc_output"]["value"]["value"]
    if not value_has_more_than_four_decimals(otc_output_value):
        changed += 1
        aggregated_transactions_collection.update_one({
                '_id': aggregated_transaction['_id']
            }, 
                {'$set': {'aggregated_outputs.heuristics.3': False}
            }, upsert=False)
print("changed transactions:", changed)