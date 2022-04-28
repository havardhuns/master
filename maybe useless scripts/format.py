import os
from time import sleep
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, bulk_api, txs_api, entities_api
from tqdm import tqdm

load_dotenv('.env')



api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
entities_api = entities_api.EntitiesApi(api_client)

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['transactions-block-500']
aggregated_outputs = db["aggregated-outputs-block-500"]
aggregated_transactions = db["aggregated-transactions"]

def get_entity_from_inputs_outputs(puts):
    for put in puts:
        entity = addresses_api.get_address_entity('btc', put["address"][0])
        if entity:
            return {"entity": entity["entity"], "no_addresses": entity["no_addresses"]}


aos = aggregated_outputs.find({})
for ao in tqdm(aos):
    count = aggregated_transactions.count_documents({"_id": ao["_id"]})
    if count == 0:
        transaction = collection.find_one({"_id": ao["_id"]})
        aggregated_transaction = {}
        aggregated_transaction["_id"] = ao["_id"]
        aggregated_transaction["tx_hash"] = ao["tx_hash"]
        input_entity = get_entity_from_inputs_outputs(transaction["inputs"])
        aggregated_transaction["aggregated_inputs"] = {"entity": input_entity}
        if ao["otc_output"]:
            output_entity = get_entity_from_inputs_outputs([ao["otc_output"]])
            aggregated_transaction["aggregated_outputs"] = {"otc_output": ao["otc_output"], "other_output": ao["other_output"], "heuristics": {"1": ao["1"], "2": ao["3"], "3": ao["3"]}, "entity": output_entity}
        else:
            aggregated_transaction["aggregated_outputs"] = None
        aggregated_transactions.insert_one(aggregated_transaction)
        sleep(1)
    