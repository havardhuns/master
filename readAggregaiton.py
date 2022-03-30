import json
import os
from time import sleep
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
aggregated_outputs = db["aggregated-outputs"]

lol = 0
for aggregated_output in aggregated_outputs.find({}):
    if aggregated_output["1"] and aggregated_output["2"] and aggregated_output["3"]:
        print(aggregated_output["1"], "|", aggregated_output["2"], "|", aggregated_output["3"])
    else:
        lol += 1
print(aggregated_outputs.count_documents({}) - lol)
print(lol)