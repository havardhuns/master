import os
from time import sleep
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
import matplotlib.pyplot as plt
import collections
import numpy as np

load_dotenv('../.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

otc_data_set_1_collection = db["otc-addresses-data-set-1-with-height"]
otc_h4_data_set_1_collection = db["data-set-1-otc-h-24"]

h12 = []
_6 = []
_7 = []
_8 = []
_9 = []


blocks = {}
for block_height in range(100000, 700001, 100000):
    h12.append(otc_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"$or": [{"heuristics.1": True}, {"heuristics.2": True}]}]}))
    _6.append(otc_h4_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"6": True}]}))
    _7.append(otc_h4_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"7": True}]}))
    _8.append(otc_h4_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"8": True}]}))
    _9.append(otc_h4_data_set_1_collection.count_documents({ "$and": [{"block_height": { "$gt": block_height - 50000, "$lt": block_height + 50000}}, {"9": True}]}))
  
n=7
r = np.arange(n)
width = 0.15
  
plt.bar(r+width*1.5, h12, color= '#9dc6e0', width = width*4, edgecolor = 'black', label="H2.1+H2.2")
  
plt.bar(r, _6, color = '#58508d',
        width = width, edgecolor = 'black',
        label='Other output not OTC addressed previously')
plt.bar(r + width, _7, color = '#bc5090',
        width = width, edgecolor = 'black',
        label='Optimal change heuristic')
plt.bar(r + width*2, _8, color = '#ff6361',
        width = width, edgecolor = 'black',
        label='Number of inputs equals 2')
plt.bar(r + width * 3, _9, color = '#ffa600',
        width = width, edgecolor = 'black',
        label='OTC value more than 4 decimals in fractional part')
  
plt.xlabel("Block height")
plt.ylabel("Number of transactions with OTC address")

# plt.grid(linestyle='--')
plt.xticks(r + width*1.5,['~100k', '~200k', '~300k', '~400k', '~500k', '~600k', '~700k', ])
plt.legend()
  
plt.show()