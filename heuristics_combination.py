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
            otc = otc_collection.find_one({"$and": [{"tx_hash": tx_hash}, {"heuristics.4": True}]})
            if otc and otc["otc_output"]["address"][0] not in entity["address_cluster"]:
                entity_with_otc_address = entities_collection.find_one({"address_cluster": otc["otc_output"]["address"][0]})
                if entity_with_otc_address and entity_with_otc_address["_id"] != entity["_id"]:
                    entities_collection.update_one({
                        '_id': entity['_id']
                    }, {
                        '$addToSet': {
                            'address_cluster': { '$each': entity_with_otc_address["address_cluster"]}
                        },
                        '$push': {
                            'tx_hashes': { '$each': entity_with_otc_address["tx_hashes"]}
                        }
                    })
                    entities_collection.delete_one({"_id": entity_with_otc_address["_id"]})

entities_collection = db['entities-data-set-2']
otc_collection = db['otc-addresses-data-set-2']

combine_entities_with_otc_address(entities_collection, otc_collection)