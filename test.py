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
'''

load_dotenv('.env')

address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
transaction_collection = db['transactions']
collection = db['linked-inputs']

transactions = transaction_collection.find({"coinbase": False})

addresses = []
for transaction in tqdm(transactions):
    addresses_in_transaction = [inp["address"][0][""]
                                for inp in transaction["inputs"]]
    addresses_in_transaction = list(
        OrderedDict.fromkeys(addresses_in_transaction))
    addresses.extend(addresses_in_transaction)
print(len(list(set(addresses))))

addresses2 = []
for lol in tqdm(collection.find({})):
    address_list = lol["addresses"]
    addresses2.extend(lol["addresses"])
print(len(list(set(addresses2))))
