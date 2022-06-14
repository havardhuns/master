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

def get_number_of_addresses(transactions):
    inputs = 0
    outputs = 0
    for transaction in transactions:
        inputs += len(transaction["inputs"])
        outputs += len(transaction["outputs"])
    return inputs, outputs

'''for height in tqdm([100000,200000, 300000, 400000,500000,600000,700000]):
    transactions = block_transactions_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    no_inputs, no_outputs = get_number_of_addresses(transactions)

    linked_inputs_collection = db[f'linked-inputs-{height}']
    linked_inputs_strict_collection = db[f'linked-inputs-{height}-strict']

    no_inputs_aggregated = linked_inputs_collection.count_documents({})
    no_inputs_strict = linked_inputs_strict_collection.count_documents({})

    heights[height] = {"total": no_inputs, "input_aggregation": no_inputs_aggregated, "input_aggregation_strict": no_inputs_strict}
print(heights)'''
heights = {100000: {'total': 11711, 'input_aggregation': 6179, 'input_aggregation_strict': 7382}, 200000: {'total': 28686, 'input_aggregation': 4323, 'input_aggregation_strict': 7506}, 300000: {'total': 28601, 'input_aggregation': 7336, 'input_aggregation_strict': 16497}, 400000: {'total': 29377, 'input_aggregation': 8456, 'input_aggregation_strict': 15206}, 500000: {'total': 19467, 'input_aggregation': 9726, 'input_aggregation_strict': 14370}, 600000: {'total': 17129, 'input_aggregation': 7348, 'input_aggregation_strict': 11423}, 700000: {'total': 35687, 'input_aggregation': 9220, 'input_aggregation_strict': 18392}}

r = np.arange(7)
width = 0.15

_total_no = []
_1 = []
_2 = []

for height in heights:
    _total_no.append(heights[height]["total"])
    _1.append(heights[height]["input_aggregation"])
    _2.append(heights[height]["input_aggregation_strict"])

print(_total_no)
print(_1)
print(_2)
  
plt.bar(r, _total_no, color = 'b',
        width = width, edgecolor = 'black',
        label='No. of original input addresses')
plt.bar(r + width, _2, color = 'r',
        width = width, edgecolor = 'black',
        label='strict')
plt.bar(r + width*2, _1, color = 'g',
        width = width, edgecolor = 'black',
        label='aggregated number')

  
plt.ylabel("Number of addresses")
plt.xlabel("Block")
plt.title("Address reduction")
  
plt.xticks(r + width,['~100000', '~200000', '~300000','~400000', '~500000', '~600000', '~700000'])
plt.legend()
plt.show()