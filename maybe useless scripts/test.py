import networkx as nx
import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from random import randint
from collections import OrderedDict


'''
Combines inputs
'''

load_dotenv('../.env')

address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
output_collection_1 = db['time-transactions']
output_collection_2 = db['transactions-block-500']

outputs_1 = output_collection_1.find({"height": 500000})

for output in outputs_1:
    output_2 = output_collection_2.find_one({"tx_hash": output["tx_hash"]})
    print(output)
    print("\n\n")
    print(output_2)
    print("\n\n\n\n")
    '''if (output != output_2):
        print(output["tx_hash"])'''
