''' WIP '''

import os
from time import sleep
from venv import create
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api, txs_api
from tqdm import tqdm
from time import time
import matplotlib.pyplot as plt

import numpy as np

load_dotenv('../.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

data_set_collection = db['data-set-1']
d1_h24_collection = db['data-set-1-otc-h-24']

total = [0,0,0]


heights = {}

def get_addresses(puts, json=False):
    addresses = []
    for put in puts:
        try:
            addresses.append(put["address"][0])
        except IndexError as e:
            continue
    return addresses

def get_number_of_addresses(transactions):
    inputs = []
    outputs = []
    for transaction in transactions:
        input_addresses = get_addresses(transaction["inputs"])
        for address in input_addresses:
            if address not in inputs:
                inputs.append(address)
        output_addresses = get_addresses(transaction["outputs"])
        for address in output_addresses:
            if address not in inputs and address not in outputs:
                outputs.append(address)
    return len(inputs), len(outputs)

def get_no_inputs_in_entity_collection(entity_collection):
    inputs = []
    entities = entity_collection.find({})
    entities = [entity for entity in entities]
    for entity in entities:
        for address in entity["address_cluster"]:
            if address not in inputs:
                inputs.append(address)
            else:
                print("wtf")
    return len(inputs)

#print(count_inputs_in_entity_collection(db['entities-data-set-2']))

_1 = []
_3 = []
_3_h24 = []

i = []
o = []

e_1 = []
e_3 = []
e_h_24 = []

def getInputsOutputs_h1():
    pass

def print_list(liste):
    for i in liste:
        print(i)
    print("")

def print_entities(number):
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in range(0, number_of_transactions, 10000):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        entity_collection = db[f'z-z-{number}-entity-{i}-{i+increment-1}-{number}']
        print(entity_collection.count_documents({}))

#print_entities(1)
        

def create_h24_d2():
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in tqdm(range(0, number_of_transactions, 10000)):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        entity_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2']
        h_24_entity_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2_h24']
        entities = entity_collection.find({}).allow_disk_use(True)
        entities = [e for e in entities]
        h_24_entity_collection.insert_many(entities)
#create_h24_d2()

def getInputsOutputs_h2():
    i_e = []
    i_ds = []
    o_ds = []

    otc = []


    inputs_ds = []
    outputs_ds = []

    data_set_2 = db['data-set-2']
    otc_collection = db['otc-addresses-data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in tqdm(range(0, number_of_transactions, 10000)):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        transactions = data_set_2.find({}).sort([("height", 1), ("_id", 1)]).skip(i).limit(10000).allow_disk_use(True)
        transactions = [t for t in transactions]
        otc.append(0)
        if i != 0:
            otc[i] += otc[i+1]
        for transaction in tqdm(transactions):
            input_addresses = get_addresses(transaction["inputs"])
            for address in input_addresses:
                if address not in inputs_ds:
                    inputs_ds.append(address)
            output_addresses = get_addresses(transaction["outputs"])
            for address in output_addresses:
                if  address not in outputs_ds and address not in inputs_ds:
                    outputs_ds.append(address)
            if otc_collection.find_one({"$and": [{"tx_hash": transaction["tx_hash"]}, {"heuristics.4": True}]}):
                otc[i] += 1
        
        entity_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2']
        no_inputs_from_entities = get_no_inputs_in_entity_collection(entity_collection)

        i_e.append(no_inputs_from_entities)
        i_ds.append(len(inputs_ds))
        o_ds.append(len(outputs_ds))


        print(i_e[i])
        print(i_ds[i])
        print(o_ds[i])
        print(otc[i])
    print("inputs from entities")
    print_list(i_e)
    print("inputs from transactions")
    print_list(i_ds)
    print("outputs from transactions")
    print_list(o_ds)
    print("otc")
    print_list(otc)

def get_otc_not_used_as_input():
    otc_col = db['otc-addresses-data-set-1-with-height']
    otc_4_col = db['data-set-1-otc-h-24']
    transactions_col = db['data-set-1']
    fml = db['z-linked-inputs-100000-3']
    otc_not_used_as_input_count = 0
    otc_datas = otc_4_col.find({"$and": [{"block_height": {"$gt": 50000, "$lt": 150000}}, {"6": True}, {"7": True}]})
    for otc_data in tqdm(otc_datas):
        otc_address = otc_col.find_one({"tx_hash": otc_data["tx_hash"]})["otc_output"]["address"][0]
        otc_not_used_as_input = fml.find_one({"address_cluster": otc_address})
        if not otc_not_used_as_input:
            otc_not_used_as_input_count += 1
    print(otc_not_used_as_input_count)

def otc_not_used_as_input_d2():
    fml = []
    otc_not_used_as_input_count = 0
    data_set_2 = db['data-set-2']
    otc_collection = db['otc-addresses-data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in range(0, number_of_transactions, 10000):
        otc_not_used_as_input_count = 0
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        transactions = data_set_2.find({}).sort([("height", 1), ("_id", 1)]).limit(i+10000).allow_disk_use(True)
        transactions = [t for t in transactions]
        entity_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2']

        for transaction in tqdm(transactions):
            otc_data = otc_collection.find_one({"tx_hash": transaction["tx_hash"]})
            if otc_data["heuristics"]["4"]:
                if not entity_collection.find_one({"address_cluster": otc_data["otc_output"]["address"][0]}):
                    otc_not_used_as_input_count += 1
        print(otc_not_used_as_input_count)
        fml.append(otc_not_used_as_input_count)
    print(fml)
otc_not_used_as_input_d2()




output_reduction = [2572, 2308, 1635, 3051, 1500, 1757]

'''for height in tqdm([100000, 300000, 400000,500000,600000,700000]):
    transactions = data_set_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})

    aggregated_transactions_collection1 = db[f'z-linked-inputs-{height}-1']
    aggregated_transactions_collection3 = db[f'z-linked-inputs-{height}-3']
    aggregated_transactions_collection3_h24 = db[f'z-linked-inputs-{height}-3_h24']


    inputs = []
    for entity in aggregated_transactions_collection1.find({}):
        for address in entity["address_cluster"]:
            if address not in inputs:
                inputs.append(address)
    i.append(len(inputs))
    outputs = []
    for transaction in transactions:
        output_addresses = get_addresses(transaction["outputs"])
        for address in output_addresses:
            if address not in inputs and address not in outputs:
                outputs.append(address)
    o.append(len(outputs))
    
    no_entities1 = aggregated_transactions_collection1.count_documents({})
    no_entities3 = aggregated_transactions_collection3.count_documents({})
    no_entities3_h24 = aggregated_transactions_collection3_h24.count_documents({})
    e_1.append(no_entities1)
    e_3.append(no_entities3)
    e_h_24.append(no_entities3_h24)
    output_address_reduction = d1_h24_collection.count_documents({"$and": [{ "block_height" : {"$gt": height-50000, "$lt": height+50000}},{"6": True}, {"7": True}]})
    print(output_address_reduction)
    _1.append(1 - ((no_entities1 + len(outputs)) / (len(inputs) + len(outputs))))
    _3.append(1 - ((no_entities3 + len(outputs)) / (len(inputs) + len(outputs))))
    _3_h24.append(1 - ((no_entities3_h24 + len(outputs) - output_address_reduction) / (len(inputs) + len(outputs))))



print_list(i)
print_list(o)
print_list(e_1)'''

_1 = [i/100 for i in [22.67, 28.40, 29.77, 19.57, 20.97, 33.02]]
_3 = [i/100 for i in [19.09, 7.40, 12.57, 8.50, 7.67, 21.55]]
_324 = [i/100 for i in [45.44, 15.42, 18.74, 19.97, 14.98, 25.15]]

r = np.arange(6)
width = 0.15

plt.bar(r, _1, color = '#003f5c',
        width = width, edgecolor = 'black',
        label='H1.1')
plt.bar(r + width, _3, color = '#ffa600',
        width = width, edgecolor = 'black',
        label='H1.3')
plt.bar(r + width*2, _324, color = '#ef5675',
        width = width, edgecolor = 'black',
        label='H1.3 + H2.4')

plt.ylabel("Ratio of address reduction")
plt.xlabel("Block")

plt.xticks(r+width,['~100000', '~300000', '~400000', '~500000', '~600000', '~700000'])
plt.yticks([i*0.1 for i in range (1,6)])
plt.legend()
plt.show()