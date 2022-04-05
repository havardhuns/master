"""docstring"""

import os
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, entities_api
from time import sleep, time
from tqdm import tqdm
import hashlib

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db["transactions-block-500"]

aggregated_inputs = db["aggregated-inputs-block-500"]

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
entities_api = entities_api.EntitiesApi(api_client)

def get_entity_from_inputs(inputs):
    for inp in inputs:
        entity = addresses_api.get_address_entity('btc', inp["address"][0])["entity"]
        if entity:
            return entity

def get_addresses_from_entity(entity):
    addresses = []
    response = entities_api.list_entity_addresses('btc', entity, pagesize=1000)
    addresses.extend(response.addresses)
    while 'next_page' in response:
        sleep(1)
        response = entities_api.list_entity_addresses('btc', entity, page=response['next_page'], pagesize=1000)
        addresses.extend(response.addresses)
    return [address["address"] for address in addresses]

transactions = collection.find({"coinbase": False})
for transaction in tqdm(transactions):
    count = aggregated_inputs.count_documents({"tx_hash": transaction["tx_hash"]})
    if count == 0:
        entity = get_entity_from_inputs(transaction["inputs"])
        entity_exist = aggregated_inputs.find_one({"_id": entity})
        if entity_exist:
            aggregated_inputs.update_one({
                        '_id': entity_exist['_id']
                    }, 
                        {'$push': {'tx_hash': transaction["tx_hash"]}
                    }, upsert=False)
        else:
            addresses = get_addresses_from_entity(entity)
            pagesize = 100000
            if len(addresses) > pagesize:
                aggregated_input =  {"_id": entity, "tx_hash": [transaction["tx_hash"]], "addresses": addresses[:pagesize]}
                aggregated_inputs.insert_one(aggregated_input)
                page = entity
                for i in range(0, len(addresses[pagesize:]), pagesize):
                    id = hashlib.sha1(str(time()).encode('utf-8')).hexdigest()
                    inserted_document = aggregated_inputs.insert_one({"_id": id, "addresses": addresses[i:pagesize]})
                    aggregated_inputs.update_one(
                        {'_id': page}, 
                        {
                            '$set': 
                                {"next_page": inserted_document.inserted_id }
                        }, upsert=False)
                    page = id
            else:
                aggregated_input = {"_id": entity, "tx_hash": [transaction["tx_hash"]], "addresses": addresses}
                aggregated_inputs.insert_one(aggregated_input)