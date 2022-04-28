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
block_transactions_collection = db["block-transactions"]
aggregated_transactions_collection = db["aggregated-transactions_new"]
entities_collection = db["entities"]

aggregated_transactions = aggregated_transactions_collection.find({})
number_of_transactions = aggregated_transactions_collection.count_documents({})

heuristics = [0,0,0,0]
extra_addresses = []
blocks = {}
i = 0
'''for aggregated_transaction in tqdm(aggregated_transactions):
    #block_transaction = block_transactions_collection.find_one({"_id": aggregated_transaction["_id"]})
    
    aggregated_outputs = aggregated_transaction["aggregated_outputs"]
    aggregated_inputs =  aggregated_transaction["aggregated_inputs"]
    input_entity = aggregated_inputs["entity"]
    if input_entity:
        entity = entities_collection.find_one({"_id": input_entity["entity"]})
        if not entity:
            entity = {"_id": input_entity["entity"], "original_no_addresses": input_entity["no_addresses"], "output_entities_1": [], "output_entities_2": [], "output_entities_3": [], "output_entities_all": []}
            if aggregated_outputs and aggregated_outputs["heuristics"]["1"]:
                entity["output_entities_1"].append(aggregated_outputs["entity"])
            if aggregated_outputs and aggregated_outputs["heuristics"]["2"]:
                entity["output_entities_2"].append(aggregated_outputs["entity"])
            if aggregated_outputs and aggregated_outputs["heuristics"]["3"]:
                entity["output_entities_3"].append(aggregated_outputs["entity"])
            if aggregated_outputs and aggregated_outputs["heuristics"]["1"] and aggregated_outputs["heuristics"]["2"] and aggregated_outputs["heuristics"]["3"]:
                entity["output_entities_all"].append(aggregated_outputs["entity"])
            entities_collection.insert_one(entity)
        else:
            if aggregated_outputs and aggregated_outputs["heuristics"]["1"]:
                if aggregated_outputs["entity"] not in entity["output_entities_1"]:
                    entities_collection.update_one({
                        '_id': input_entity["entity"]
                    }, 
                        {'$push': {'output_entities_1': aggregated_outputs["entity"]}
                }, upsert=False)
            if aggregated_outputs and aggregated_outputs["heuristics"]["2"]:
                if aggregated_outputs["entity"] not in entity["output_entities_2"]:
                    entities_collection.update_one({
                        '_id': input_entity["entity"]
                    }, 
                        {'$push': {'output_entities_2': aggregated_outputs["entity"]}
                }, upsert=False)
            if aggregated_outputs and aggregated_outputs["heuristics"]["3"]:
                if aggregated_outputs["entity"] not in entity["output_entities_3"]:
                    entities_collection.update_one({
                        '_id': input_entity["entity"]
                    }, 
                        {'$push': {'output_entities_3': aggregated_outputs["entity"]}
                }, upsert=False)
            if aggregated_outputs and aggregated_outputs["heuristics"]["1"] and aggregated_outputs["heuristics"]["2"] and aggregated_outputs["heuristics"]["3"]:
                if aggregated_outputs["entity"] not in entity["output_entities_all"]:
                    entities_collection.update_one({
                        '_id': input_entity["entity"]
                    }, 
                        {'$push': {'output_entities_all': aggregated_outputs["entity"]}
                }, upsert=False)'''

entities = entities_collection.find({})

number_of_entities = entities_collection.count_documents({})

intput_entities_sum = 0
entities_1 = 0
entities_2 = 0
entities_3 = 0
entities_all = 0

no_entities_1 = 0
no_entities_2 = 0
no_entities_3 = 0
no_entities_all = 0

for entity in entities:
    if entity["original_no_addresses"] < 100000:
        intput_entities_sum += entity["original_no_addresses"]
        entities_1 += entity["original_no_addresses"]
        entities_2 += entity["original_no_addresses"]
        entities_3 += entity["original_no_addresses"]
        entities_all += entity["original_no_addresses"]
    for oe in entity["output_entities_1"]:
        if oe["entity"] != entity["_id"] and oe["no_addresses"] < 100000:
            entities_1 += oe["no_addresses"]
            no_entities_1 += 1 
    for oe in entity["output_entities_2"]:
        if oe["entity"] != entity["_id"] and oe["no_addresses"] < 100000:
            entities_2 += oe["no_addresses"]
            no_entities_2 += 1
    for oe in entity["output_entities_3"]:
        if oe["entity"] != entity["_id"] and oe["no_addresses"] < 100000:
            entities_3 += oe["no_addresses"]
            no_entities_3 += 1
    for oe in entity["output_entities_all"]:
        if oe["entity"] != entity["_id"] and oe["no_addresses"] < 100000:
            entities_all += oe["no_addresses"]
            no_entities_all += 1

plot = [intput_entities_sum/number_of_entities, entities_1/(number_of_entities+no_entities_1), entities_2/(number_of_entities+no_entities_2), entities_3/(number_of_entities+no_entities_3), entities_all/(number_of_entities+no_entities_all)]

plt.bar(["i", "i+1", "i+2", "i+3", "i+all"], plot)
plt.show()
