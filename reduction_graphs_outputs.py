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

_100k = [2942, 3425, 75, 3315]
_300k = [3298, 3673, 2147, 2323]
_400k = [2470, 2713, 1680, 1600]
_500k = [3408, 4421, 2867, 3622]
_600k = [1866, 2139, 1600, 1713]
_700k = [2240, 2546, 1904, 1948]

wow = [3315, 2323, 1600, 3622, 1713, 1948]

total = [0,0,0]


heights = {}

def get_addresses(puts, json=False):
    addresses = []
    for put in puts:
        try:
            addresses.append(put["address"][0])
        except IndexError as e:
            continue
    return addresses

def get_number_of_addresses(transactions):
    inputs = []
    outputs = []
    for transaction in transactions:
        input_addresses = get_addresses(transaction["inputs"])
        for address in input_addresses:
            if address not in inputs:
                inputs.append(address)
        output_addresses = get_addresses(transaction["outputs"])
        for address in output_addresses:
            if address not in inputs:
                if address not in outputs:
                        outputs.append(address)
    return len(inputs), len(outputs)

for index, height in enumerate([100000, 300000, 400000,500000,600000,700000]):
    print("lol")
    transactions = block_transactions_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    no_inputs, no_outputs = get_number_of_addresses(transactions)

    ggregated_transactions_collection = db[f'linked-inputs-{height}-1']
    aggregated_transactions_collection2 = db[f'linked-inputs-{height}-3']

    no_entities1 = ggregated_transactions_collection.count_documents({})
    no_entities2 = aggregated_transactions_collection2.count_documents({})

    total[0] += no_inputs + no_outputs
    total[1] += no_entities1 + no_outputs
    total[2] += no_entities2 + no_outputs-wow[index]

    heights[height] = { "total": no_inputs + no_outputs, "heuristics": [no_entities1 + no_outputs, no_entities2 + no_outputs-wow[index]]}


r = np.arange(6)
width = 0.15

_1 = []
_2 = []

for height in heights:
    total_no = heights[height]["total"]
    _1.append((total_no - heights[height]["heuristics"][0]) / total_no)
    _2.append((total_no - heights[height]["heuristics"][1]) / total_no)

  
plt.bar(r, _1, color = 'b',
        width = width, edgecolor = 'black',
        label='H1.1')
plt.bar(r + width, _2, color = 'g',
        width = width, edgecolor = 'black',
        label='H1.3 + H2.4')


print(total)

plt.ylabel("Ratio of address reduction")
plt.xlabel("Block")
plt.title("Address reduction")
  
plt.xticks(r+width*0.5,['~100000', '~300000', '~400000', '~500000', '~600000', '~700000'])
plt.legend()
plt.show()