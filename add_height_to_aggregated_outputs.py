import os
from time import sleep
import graphsense
from numpy import block
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, bulk_api, txs_api, entities_api
from tqdm import tqdm
from aggregate_outputs import value_has_more_than_four_decimals, has_been_otc_addressed_previously

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
aggregated_transactions_new = db["aggregated-transactions_new"]
collection = db['block-transactions']
changed = 0
aggregated_transactions = aggregated_transactions_collection.find()

for aggregated_transaction in tqdm(aggregated_transactions):
    count = aggregated_transactions_new.count_documents({"_id" : aggregated_transaction["_id"]})
    if count == 0:
        transaction = collection.find_one({"_id": aggregated_transaction["_id"]})
        new_document = {"_id": aggregated_transaction["_id"], "tx_hash": aggregated_transaction["tx_hash"], "height": transaction["height"], "aggregated_inputs": aggregated_transaction["aggregated_inputs"], "aggregated_outputs": aggregated_transaction["aggregated_outputs"]}
        aggregated_transactions_new.insert_one(new_document)


'''
[113, 3251, 0]
[113, 3360, 0]
'''