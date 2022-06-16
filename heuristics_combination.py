import pymongo
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

def combine_entities_with_otc_address(entities_collection, otc_collection):
    entities = entities_collection.find({})
    entities = [entity for entity in entities]
    for entity in tqdm(entities):
        for tx_hash in entity["tx_hashes"]:
            otc = otc_collection.find_one({"tx_hash": tx_hash})
            if otc["heuristics"]["4"] and otc["otc_output"]["address"][0] not in entity["address_cluster"]:
                entity_with_otc_address = entities_collection.find_one({"address_cluster": otc["otc_output"]["address"][0]})
                if entity_with_otc_address and entity_with_otc_address["_id"] != entity["_id"]:
                    entities_collection.update_one({
                        '_id': entity['_id']
                    }, {
                        '$addToSet': {
                            'address_cluster': { '$each': entity_with_otc_address[ "address_cluster"]}
                        },
                        '$push': {
                            'tx_hashes': { '$each': entity_with_otc_address["tx_hashes"]}
                        }
                    })
                    entities_collection.delete_one({"_id": entity_with_otc_address["_id"]})

def combine_d1():
    otc_collection = db['data-set-1-otc-h-24']
    for block_height in range(100000, 700001, 100000):
        entities_collection = db[f'z-linked-inputs-{block_height}-3_h24']
        combine_entities_with_otc_address(entities_collection, otc_collection)

def combine_d2():
    otc_collection = db['otc-addresses-data-set-2']
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in tqdm(range(80000, number_of_transactions, 10000)):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        entities_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2_h24']
        combine_entities_with_otc_address(entities_collection, otc_collection)

combine_d2()