import networkx as nx
import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from random import randint
from collections import OrderedDict
import graphsense
from graphsense.api import txs_api
import json

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

txs_api = txs_api.TxsApi(api_client)


connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['transactions']
newCollection = db['transactions-block-500']

transactions = collection.find(
    {"height": 500000, "coinbase": False}, no_cursor_timeout=True, batch_size=10)

def formatInputOutput(puts):
    fml = []
    for put in puts:
        address = []
        if put["address"]:
            address = [put["address"][0][""]]
        fml.append({"address": address, "value": {"fiat_values" : put["value_fiat_values"], "value": put["value_value"]}})
    return fml
    


for transaction in tqdm(transactions):
    try:
        transaction["inputs"] = formatInputOutput(transaction["inputs"])
    except IndexError as e:
        print("input error")
        print(transaction["tx_hash"])
        continue
    try:
        transaction["outputs"] = formatInputOutput(transaction["outputs"])
    except IndexError as e:
        print("output error")
        print(transaction["tx_hash"])
        continue
    transaction["total_input"] = {"fiat_values": transaction["total_input_fiat_values"], "value": transaction["total_input_value"]}
    transaction["total_output"] = {"fiat_values": transaction["total_output_fiat_values"], "value": transaction["total_output_value"]}
    del transaction["request_tx_hash"]
    del transaction["total_input_fiat_values"]
    del transaction["total_input_value"]
    del transaction["total_output_fiat_values"]
    del transaction["total_output_value"]
    newCollection.insert_one(transaction)