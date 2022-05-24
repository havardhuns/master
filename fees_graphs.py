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

block_transactions = block_transactions_collection.find({"coinbase": False})

blocks = {} 
for transaction in tqdm(block_transactions):
    height = str(round(transaction["height"], -5))
    if height not in blocks:
        blocks[height] = {"btc": [], "usd": []}
    fee_btc = transaction["total_input"]["value"]*10**(-8) - transaction["total_output"]["value"]*10**(-8)
    fee_usd =  transaction["total_input"]["fiat_values"][1]["value"] - transaction["total_output"]["fiat_values"][1]["value"]
    blocks[height]["btc"].append(fee_btc)
    blocks[height]["usd"].append(fee_usd)


for block in blocks:
    fee_list = blocks[block]
    fee_btc = sorted(blocks[block]["btc"])
    fee_usd = sorted(blocks[block]["usd"])
    blocks[block]["btc"] = (sum(fee_btc) / len(fee_btc))
    blocks[block]["usd"] = (sum(fee_usd) / len(fee_usd))

fees = [blocks[block]["btc"] for block in blocks]

labels = ["100k", "200k", "300k", "400k", "500k", "600k", "700k"]
plt.bar(labels, fees)
plt.xlabel("Fee")
plt.ylabel("Block")
plt.grid(axis = 'y')
plt.show()