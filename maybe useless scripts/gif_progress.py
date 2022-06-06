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
block_transactions_collection = db["block-transactions"]
aggregated_transactions_collection = db["aggregated-transactions_new"]

number_of_transactions = aggregated_transactions_collection.count_documents({})
aggregated_transactions = aggregated_transactions_collection.find({})

transactions = [0,0,0,0,0,0,0]
aggregated = [0,0,0,0,0,0,0]
i = 0
while i < 7:
    height = (i+1)*100000
    transactions[i] = block_transactions_collection.count_documents({"height": {"$gt": height - 50000, "$lt": height+50000}})
    i+=1


labels = ["100k", "200k", "300k", "400k", "500k", "600k", "700k"]
filenames = []


for index, transaction in enumerate(aggregated_transactions):
    i = int(round(transaction["height"], -5)/100000)-1
    aggregated[i] += 1
    if index%1000 == 0:
        fig, ax = plt.subplots()
        width = 0.35
        ax.bar(labels, transactions, width, color="grey")
        ax.bar(labels, aggregated, width, color="green")
        ax.set_ylabel('Number of transactions')
        ax.set_xlabel('Block')
        ax.set_title(f'Number of transactions: {index+1}')
        filename = f'graphs/gif/{index}.png'
        filenames.append(filename)
        plt.legend()
        plt.grid(axis = 'y')
        plt.savefig(filename)
        plt.close()


images = []
for file_name in filenames:
        images.append(imageio.imread(file_name))
imageio.mimsave('movie.gif', images)