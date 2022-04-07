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
collection = db['unique-inputs']

transactions = transaction_collection.find({"coinbase": False})

for transaction in tqdm(transactions):
    addresses_in_transaction = list(
        set([inp["address"][0][""] for inp in transaction["inputs"]]))
    addresses_in_transaction.sort()
    matching = collection.find_one({"addresses": addresses_in_transaction})
    if not matching:
        collection.insert_one(
            {"addresses": addresses_in_transaction})
