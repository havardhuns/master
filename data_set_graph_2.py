''' WIP '''

import os
from time import sleep
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time
import matplotlib.pyplot as plt
import collections
import imageio

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
block_transactions_collection = db["new-time-transactions"]

number_of_transactions = block_transactions_collection.count_documents({})

transactions = []
heights = list(range(721253, 721407))
for height in tqdm(heights):
   transactions.append(block_transactions_collection.count_documents({"height": height}))

fig, ax = plt.subplots()
width = 0.35
ax.bar(heights, transactions)
ax.set_ylabel('Number of transactions')
ax.set_xlabel('Block')
ax.set_title(f'Number of transactions: {number_of_transactions}')

plt.legend()
plt.grid(axis = 'y')
plt.show()