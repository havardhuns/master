import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv


load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
aggregated_outputs_collection = db["aggregated-transactions"]
proposed_otc_collection = db["proposed-otc"]


for height in range(100000, 700001, 100000):
    otc_addresses = []
    aggregated_outputs = [0,0,0,0]
    collection = db[f'linked-inputs-{height}-3']
    linked_inputs = collection.find({})
    for linked_input in tqdm(linked_inputs):
        for tx_hash in linked_input["tx_hashes"]:
            aggregated_output = aggregated_outputs_collection.find_one({"tx_hash": tx_hash})
            if aggregated_output and aggregated_output["aggregated_outputs"] is not None:
                address = aggregated_output["aggregated_outputs"]["otc_output"]["address"][0]
                if address not in linked_input["aggregated_inputs_3"]:
                    if address not in otc_addresses:
                        otc_addresses.append(address)
                        if aggregated_output["aggregated_outputs"]["heuristics"]["1"]:
                            aggregated_outputs[0] += 1
                        if aggregated_output["aggregated_outputs"]["heuristics"]["1"] or aggregated_output["aggregated_outputs"]["heuristics"]["2"]:
                            aggregated_outputs[1] += 1
                        if aggregated_output["aggregated_outputs"]["heuristics"]["3"]:
                            aggregated_outputs[2] += 1
                        aggregated_output_4 = proposed_otc_collection.find_one({"tx_hash": tx_hash})
                        if aggregated_output_4 and aggregated_output_4["6"] and aggregated_output_4["7"] and aggregated_output_4["8"]:
                            aggregated_outputs[3] += 1
    print(aggregated_outputs)