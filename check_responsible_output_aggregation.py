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
collection = db['block-transactions']
changed = 0
aggregated_transactions = aggregated_transactions_collection.find( { "$or": [ { 'aggregated_outputs.heuristics.1': True }, { 'aggregated_outputs.heuristics.2': True } ] } )
feil = [0,0,0]

for aggregated_transaction in tqdm(aggregated_transactions):
    transaction = collection.find_one({"$and": [{"_id": aggregated_transaction["_id"]}, { "height" : { "$gt" :  98826, "$lt" : 101175}}]})
    if transaction:
        # (3) The number of t inputs is not equal to two.
        if len(transaction['inputs']) == 2:
            feil[0] += 1
        # (6) Decimal representation of the value for address O has more than 4 digits after the dot.
        if not value_has_more_than_four_decimals(aggregated_transaction["aggregated_outputs"]["otc_output"]["value"]["value"]):
            feil[1] += 1
        # (9) ~O has not been OTC addressed in previous transactions
        '''if has_been_otc_addressed_previously(aggregated_transaction["aggregated_outputs"]["other_output"]["address"][0]):
            feil[2] += 1'''


'''
[113, 3251, 0]
[113, 3360, 0]
'''