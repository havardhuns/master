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
prop_db = db["proposed-otc"]

aggregated_transactions = aggregated_transactions_collection.find({})
number_of_transactions = aggregated_transactions_collection.count_documents({})

heuristics = [0,0,0, 0]
entities = {}
extra_addresses = []
blocks = {}
heights = []
for aggregated_transaction in tqdm(aggregated_transactions):
    height = str(round(aggregated_transaction["height"], -5))
    if height != "200000":
        if height not in blocks:
            blocks[height] = {"heuristics": [0,0,0, 0], "entities": [0,0], "extra_addresses": 0}
        aggregated_outputs = aggregated_transaction["aggregated_outputs"]
        aggregated_inputs =  aggregated_transaction["aggregated_inputs"]
        if aggregated_outputs:
            if aggregated_outputs["heuristics"]["1"] or aggregated_outputs["heuristics"]["2"]:
                blocks[height]["heuristics"][0] += 1
                blocks[height]["heuristics"][1] += 1
                blocks[height]["heuristics"][2] += 1
                blocks[height]["heuristics"][3] += 1
                proposed = prop_db.find_one({"tx_hash": aggregated_transaction["tx_hash"]})
                if not proposed["6"]: 
                    blocks[height]["heuristics"][1] -= 1
                    blocks[height]["heuristics"][2] -= 1
                    blocks[height]["heuristics"][3] -= 1
                if not proposed["7"]: 
                    blocks[height]["heuristics"][2] -= 1
                    blocks[height]["heuristics"][3] -= 1
                if not proposed["8"]: 
                    blocks[height]["heuristics"][3] -= 1

def sum_lists(first, second):
    return [x + y for x, y in zip(first, second)]




'''for entity in entities:
    if len(entities[entity]["output_entities"]) > 2:
        print(entities[entity])'''

'''height = block_transaction["height"]
    if height not in blocks:
        blocks[height] = {heuristics: [0,0,0,0], entities: [0,0], extra_addresses: []}
    aggregated_outputs = aggregated_transaction["aggregated_outputs"]
    aggregated_inputs =  aggregated_transaction["aggregated_inputs"]
    if aggregated_outputs["heuristics"]["1"]:
        blocks[height]["heuristics"][0] += 1
    if aggregated_outputs["heuristics"]["2"]:
        blocks[height]["heuristics"][1] += 1
    if aggregated_outputs["heuristics"]["3"]:
        blocks[height]["heuristics"][2] += 1
    if (aggregated_outputs["heuristics"]["1"] and aggregated_outputs["heuristics"]["2"] and aggregated_outputs["3"]):
        blocks[height]["heuristics"][3] += 1
        if aggregated_inputs["entity"] == aggregated_outputs["entity"]:
            blocks[height]["entities"][0] += 1
        else:
            blocks[height]["entities"][1] += 1
            blocks[height]["extra_addresses"] += aggregated_outputs["entity"]["total_tx"]'''

blocks = collections.OrderedDict(sorted(blocks.items()))

labels = ["H2.1 + H2.2", "+ (6)", "+ (7)", "+ (8)"]
fig, ax = plt.subplots()
width = [0.35, 0.15, 0.15, 0.15]
bottom = [0,0,0,0]
lol = False
x_pos = [0.35, 1, 1.5,2]
for block in blocks:
    ax.bar(x_pos, blocks[block]["heuristics"], width, label=f'Block ~{str(block)}', bottom = bottom)
    ax.set_xticks(x_pos, labels)
    bottom = sum_lists(bottom, blocks[block]["heuristics"])
ax.set_ylabel('Number of transactions')
ax.set_xlabel('Additional factors')
ax.set_title(f'Effect of additional factors on H2.1+H2.2')
plt.legend()
plt.grid(axis = 'y')
plt.show()