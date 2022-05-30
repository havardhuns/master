import networkx as nx
import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from random import randint
from collections import OrderedDict


'''
Combines inputs

The common-input-ownership heuristic (also called the multi-input heuristic
, Nakamoto/Meiklejohn heuristic or co-spending heuristic) is a heuristic or
 assumption that all inputs to a transaction are owned by the same entity.
'''

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
transaction_collection = db['block-transactions']
aggregated_outputs_collection = db["aggregated-transactions"]

def get_inputs(inputs):
    addresses = []
    for inp in inputs:
        try:
            addresses.append(inp["address"][0])
        except IndexError as e:
            continue
    return addresses

for height in range(100000, 700001, 100000):
    transactions = transaction_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    collection = db[f'linked-inputs-{height}-1']

    for transaction in tqdm(transactions):
        inputs = get_inputs(transaction["inputs"])
        if inputs:
            inputs = list(
                OrderedDict.fromkeys(inputs))
            exists = False
            for address in inputs:
                matching = collection.find_one({"aggregated_inputs_1": address})
                if matching:
                    exists = True
                    collection.update_one({
                                '_id': matching['_id']
                            }, {
                                '$push': {
                                    'tx_hashes': transaction["tx_hash"]
                                }
                            }, upsert=False)
                    old_list = matching["aggregated_inputs_1"]
                    if set(old_list) != set(matching):
                        old_list.extend(
                            address for address in inputs if address not in old_list)
                        try:
                            collection.update_one({
                                '_id': matching['_id']
                            }, {
                                '$set': {
                                    'aggregated_inputs_1': old_list
                                }
                            }, upsert=False)
                        except pymongo.errors.WriteError as e:
                            print("writeError, update")
                            print(matching)
                    break
            if not exists:
                try:
                    collection.insert_one(
                        {"_id": inputs[0], "aggregated_inputs_1": inputs, "tx_hashes": [transaction["tx_hash"]]})
                    collection.create_index("aggregated_inputs_1")
                except pymongo.errors.WriteError as e:
                    print("writeError, insert")
                    print(transaction["_id"])
            
                




