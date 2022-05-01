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

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
block_transactions_collection = db["block-transactions"]
aggregated_transactions_collection = db["aggregated-transactions_new"]

transactions = [0,0,0,0,0,0,0]
aggregated = [0,0,0,0,0,0,0]
i = 0
while i < 7:
    height = (i+1)*100000
    transactions[i] = block_transactions_collection.count_documents({"height": {"$gt": height - 50000, "$lt": height+50000}})
    aggregated[i] = aggregated_transactions_collection.count_documents({"height": {"$gt": height - 50000, "$lt": height+50000}})
    i+=1
labels = ["100k", "200k", "300k", "400k", "500k", "600k", "700k"]


labels = ["100k", "200k", "300k", "400k", "500k", "600k", "700k"]
fig, ax = plt.subplots()
width = 0.35
ax.bar(labels, transactions, width, color="grey")
ax.bar(labels, aggregated, width, color="green")
ax.set_ylabel('Number of transactions')
ax.set_xlabel('Block')
plt.legend()
plt.grid(axis = 'y')
plt.show()