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
aggregated_transactions_collection = db["linked-inputs-100000"]
aggregated_transactions = aggregated_transactions_collection.find({})

heights = {}

def get_number_of_addresses(transactions):
    inputs = 0
    outputs = 0
    for transaction in transactions:
        inputs += len(transaction["inputs"])
        outputs += len(transaction["outputs"])
    return inputs, outputs

for height in [100000,400000,500000,600000,700000]:
    transactions = block_transactions_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    no_inputs, no_outputs = get_number_of_addresses(transactions)

    aggregated_transactions_collection = db[f'linked-inputs-{height}']

    no_addresses = aggregated_transactions_collection.count_documents({})

    heights[height] = {"total": no_inputs+no_outputs, "input_aggregation": no_addresses + no_outputs, "heuristics": [no_addresses + no_outputs, no_addresses + no_outputs, no_addresses + no_outputs, no_addresses + no_outputs]}

    aggregated_transactions = aggregated_transactions_collection.find({})
    for transaction in tqdm(aggregated_transactions):
        if transaction["aggregated_outputs"]:
            heights[height]["heuristics"][0] -= len([ao for ao in transaction["aggregated_outputs"] if ao["heuristics"]["1"]])
            heights[height]["heuristics"][1] -= len([ao for ao in transaction["aggregated_outputs"] if ao["heuristics"]["2"]])
            heights[height]["heuristics"][2] -= len([ao for ao in transaction["aggregated_outputs"] if ao["heuristics"]["3"]])
            heights[height]["heuristics"][3] -= len([ao for ao in transaction["aggregated_outputs"] if ao["heuristics"]["1"] and ao["heuristics"]["2"] and ao["heuristics"]["3"]])
print(heights)

r = np.arange(5)
width = 0.15

_input = []
_1 = []
_2 = []
_3 = []
_all = []

for height in heights:
    total_no = heights[height]["total"]
    _input.append(1-(heights[height]["input_aggregation"] / total_no))
    _1.append(1-(heights[height]["heuristics"][0] / total_no))
    _2.append(1-(heights[height]["heuristics"][1] / total_no))
    _3.append(1-(heights[height]["heuristics"][2] / total_no))
    _all.append(1-(heights[height]["heuristics"][3] / total_no))

print(_input)
print(_1)
print(_2)
print(_3)
print(_all)
  
plt.bar(r, _input, color = 'b',
        width = width, edgecolor = 'black',
        label='Input aggregation')
plt.bar(r + width, _1, color = 'g',
        width = width, edgecolor = 'black',
        label='Input aggregation + Heuristic 1')
plt.bar(r + width*2, _2, color = 'r',
        width = width, edgecolor = 'black',
        label='Input aggregation + Heuristic 2')
plt.bar(r + width*3, _3, color = 'y',
        width = width, edgecolor = 'black',
        label='Input aggregation + Heuristics 3')
plt.bar(r + width*4, _all, color = 'm',
        width = width, edgecolor = 'black',
        label='Input aggregation + H1 * H2 * H3')


  
plt.ylabel("Ratio of address reduction")
plt.xlabel("Block")
plt.title("Address reduction")
  
plt.xticks(r + width*2,['100000','400000', '500000', '600000', '700000'])
plt.legend()
plt.savefig('graphs/reduction')
plt.close()