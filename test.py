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

load_dotenv('.env')

address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
output_collection_1 = db['aggregated-outputs-block-500']
output_collection_2 = db['aggregated-outputs-block-500-old']

outputs_1 = output_collection_1.find({})

for output in outputs_1:
    output_2 = output_collection_2.find_one({"tx_hash": output["tx_hash"]})
    if (output != output_2):
        print(output["tx_hash"])
