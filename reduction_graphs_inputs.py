''' WIP '''

import os
from time import sleep
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time
import matplotlib.pyplot as plt

import numpy as np

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]


block_transactions_collection = db["block-transactions"]

heights = {}

def get_addresses(puts, json=False):
    addresses = []
    for put in puts:
        try:
            addresses.append(put["address"][0])
        except IndexError as e:
            print("lol")
            continue
    return addresses

def get_number_of_input_addresses(transactions):
    inputs = []
    for transaction in transactions:
        addresses = get_addresses(transaction["inputs"])
        for address in addresses:
            if address not in inputs:
                inputs.append(address)
    print(len(inputs))
    return len(inputs)


for height in tqdm([100000, 300000, 400000,500000,600000,700000]):
    transactions = block_transactions_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    aggregated_transactions_collection_1 = db[f'linked-inputs-{height}-1']
    aggregated_transactions_collection_2 = db[f'linked-inputs-{height}-2']
    aggregated_transactions_collection_3 = db[f'linked-inputs-{height}-3']

    no_inputs = get_number_of_input_addresses(transactions)

    no_entities_1 = aggregated_transactions_collection_1.count_documents({})
    no_entities_2 = aggregated_transactions_collection_2.count_documents({})
    no_entities_3 = aggregated_transactions_collection_3.count_documents({})

    heights[height] = {"total": no_inputs, "input_aggregation": [no_entities_1, no_entities_2, no_entities_3]}


r = np.arange(6)
width = 0.25

_1 = []
_2 = []
_3 = []

for height in heights:
    total_no = heights[height]["total"]
    _1.append((total_no - heights[height]["input_aggregation"][0]) / total_no)
    _2.append((total_no - heights[height]["input_aggregation"][1]) / total_no)
    _3.append((total_no - heights[height]["input_aggregation"][2]) / total_no)
  
plt.bar(r, _1, color = 'b',
        width = width, edgecolor = 'black',
        label='H1.1')
plt.bar(r + width, _2, color = 'g',
        width = width, edgecolor = 'black',
        label='H1.2')
plt.bar(r + width*2, _3, color = 'r',
        width = width, edgecolor = 'black',
        label='H1.3')
  
plt.ylabel("Ratio of address reduction")
plt.xlabel("Block")
plt.title("Address reduction")
  
plt.xticks(r + width,['~100000', '~300000', '~400000', '~500000', '~600000', '~700000'])
plt.legend()
plt.show()