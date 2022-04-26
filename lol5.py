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

aggregated_transactions_collection = db["linked-inputs-100000"]
aggregated_transactions = aggregated_transactions_collection.find({})

reduction = [1, 1]

for transaction in tqdm(aggregated_transactions):
    