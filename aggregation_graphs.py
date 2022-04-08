''' WIP '''

import os
from time import sleep
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time
import matplotlib.pyplot as plt

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
aggregated_outputs = db["aggregated-outputs-block-500"]
lol = [0,0,0,0]
for aggregated_output in aggregated_outputs.find({}):
    if aggregated_output["1"]:
        lol[0] += 1
    if aggregated_output["2"]:
        lol[1] += 1
    if aggregated_output["3"]:
        lol[2] += 1
    if (aggregated_output["1"] and aggregated_output["2"] and aggregated_output["3"]):
        lol[3] += 1

plt.bar(["1", "2", "3", "all"], lol)
plt.title("ahm")
plt.show()