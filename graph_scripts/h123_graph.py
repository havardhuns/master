''' WIP '''

import os
from time import sleep
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
import matplotlib.pyplot as plt
import collections

load_dotenv('../.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

data_set_collection = db['data-set-1']
otc_data_set_1_collection = db["otc-addresses-data-set-1-with-height"]
otc_h4_data_set_1_collection = db["data-set-1-otc-h-24"]

number_of_transactions = data_set_collection.count_documents({})



blocks = {}
for block_height in range(100000, 700001, 100000):
    h1 = otc_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"heuristics.1": True}]})
    h2 = otc_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"heuristics.2": True}]})
    h3 = otc_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"heuristics.3": True}]})
    h4 = otc_h4_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"6": True}, {"7": True}]})
    blocks[str(block_height)] = [h1, h2, h3, h4]

def sum_lists(first, second):
    return [x + y for x, y in zip(first, second)]

labels = ["H2.1", "H2.2", "H2.3", "H2.4"]
fig, ax = plt.subplots()
width = 0.35
bottom = [0,0,0,0]
colors = ["#003f5c", "#374c80", "#7a5195", "#bc5090", "#ef5675", "#ff764a", "#ffa600"]
for i, block in enumerate(blocks):
    ax.bar(labels, blocks[block], width, label=f'Block ~{str(block)}', bottom = bottom, edgecolor="black", color=colors[i])
    bottom = sum_lists(bottom, blocks[block])
ax.set_ylabel('Number of transactions')
ax.set_xlabel('Heuristic')
ax.set_title(f'Transactions with OTC address based on heuristics. \nNumber of transactions: {number_of_transactions}')

plt.yticks([tick for tick in range(0, 18001, 2000)])
plt.legend()
plt.show()