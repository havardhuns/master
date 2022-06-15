''' WIP '''

import os
from time import sleep
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


transactions_collection = db["data-set-1"]

heights = {}

def get_addresses(puts, json=False):
    addresses = []
    for put in puts:
        try:
            addresses.append(put["address"][0])
        except IndexError as e:
            continue
    return addresses

def get_addresses_all(transactions):
    addresses = []
    input_addresses_list = []
    output_addresses_list = []
    for transaction in transactions:
        input_addresses = get_addresses(transaction["inputs"])
        for input_address in input_addresses:
            if input_address not in addresses:
                addresses.append(input_address)
                input_addresses_list.append(input_address)
        output_addresses = get_addresses(transaction["outputs"])
        for output_address in output_addresses:
            if output_address not in addresses:
                addresses.append(output_address)
                output_addresses_list.append(output_address)
    print(len(addresses), len(input_addresses_list), len(output_addresses_list))
    return addresses, input_addresses_list, output_addresses_list


data_set_2 = db['data-set-2']
number_of_transactions = data_set_2.count_documents({})
all_addresses = []
input_addresses = []
output_addresses = []

no_input_addresses = []
no_output_addresses = []

for i in range(0, number_of_transactions, 10000):
    increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
    transactions = data_set_2.find({}).sort([("height", 1), ("_id", 1)]).skip(i).limit(10000).allow_disk_use(True)
    transactions = [transactions for transactions in transactions]
    addresses, new_input_addresses, new_output_addresses = get_addresses_all(transactions)
    for address in addresses:
        if address not in all_addresses:
            all_addresses.append(address)
        if address in new_input_addresses:
            input_addresses.append(address)
        if address in new_output_addresses:
            output_addresses.append(address)
    print("i", i)
    print(len(all_addresses))
    print(len(input_addresses))
    print(len(output_addresses))
    print("")
    no_input_addresses.append(len(input_addresses))
    no_output_addresses.append(len(output_addresses))
print("\n\n\n")
print("number of input addresses:")
for no in no_input_addresses:
    print(no)
print("\n\n\n")
print("number of output addresses:")
for no in no_output_addresses:
    print(no)

'''
_1 = []
_2 = []
_3 = []

for height in tqdm([100000, 300000, 400000,500000,600000,700000]):
    transactions = transactions_collection.find({ "height" : {"$gt": height-50000, "$lt": height+50000}})
    no_inputs = get_number_of_input_addresses(transactions)

    aggregated_transactions_collection_1 = db[f'z-linked-inputs-{height}-1']
    aggregated_transactions_collection_2 = db[f'z-linked-inputs-{height}-2']
    aggregated_transactions_collection_3 = db[f'z-linked-inputs-{height}-3']

    no_entities_1 = aggregated_transactions_collection_1.count_documents({})
    no_entities_2 = aggregated_transactions_collection_2.count_documents({})
    no_entities_3 = aggregated_transactions_collection_3.count_documents({})

    _1.append(1 - (no_entities_1 / no_inputs))
    _2.append(1 - (no_entities_2 / no_inputs))
    _3.append(1 - (no_entities_3 / no_inputs))



r = np.arange(6)
width = 0.25

plt.bar(r, _1, color = 'b',
        width = width, edgecolor = 'black',
        label='H1.1')
plt.bar(r + width, _2, color = 'g',
        width = width, edgecolor = 'black',
        label='H1.2')
plt.bar(r + width*2, _3, color = 'r',
        width = width, edgecolor = 'black',
        label='H1.3')
  
plt.ylabel("Ratio of address reduction")
plt.xlabel("Block")
plt.title("Address reduction")
  
plt.xticks(r + width,['~100000', '~300000', '~400000', '~500000', '~600000', '~700000'])
plt.legend()
plt.show()'''