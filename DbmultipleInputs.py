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

address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
transaction_collection = db['transactions']
collection = db['linked-inputs-test']

transactions = transaction_collection.find(
    {"coinbase": False}, no_cursor_timeout=True, batch_size=10)

for transaction in tqdm(transactions):
    addresses_in_transaction = [inp["address"][0][""]
                                for inp in transaction["inputs"]]
    addresses_in_transaction = list(
        OrderedDict.fromkeys(addresses_in_transaction))
    exists = False
    for address in addresses_in_transaction:
        matching = collection.find_one({"addresses": address})
        if matching:
            exists = True
            old_list = matching["addresses"]
            if set(old_list) != set(matching):
                old_list.extend(
                    address for address in addresses_in_transaction if address not in old_list)
                try:
                    collection.update_one({
                        '_id': matching['_id']
                    }, {
                        '$set': {
                            'addresses': old_list
                        }
                    }, upsert=False)
                except pymongo.errors.WriteError as e:
                    print("writeError, update")
                    print(matching)
            break
    if not exists:
        try:
            collection.insert_one(
                {"_id": addresses_in_transaction[0], "addresses": addresses_in_transaction})
            collection.create_index("addresses")
        except pymongo.errors.WriteError as e:
            print("writeError, insert")
            print(transaction["_id"])
transactions.close()
