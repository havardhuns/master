import networkx as nx
import pymongo
from tqdm import tqdm


address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = "mongodb://havardhuns:pwd@10.212.136.61/master?retryWrites=true&w=majority"
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['transactions']
addresses = db['addresses']
addresses_collection = db[f'nodes-{address}']

transactions = collection.find({})


edges = []
nodes = [address["_id"]
         for address in addresses.find({})]

transactions = collection.find({"coinbase": False})
for transaction in tqdm(transactions):
    for inp in transaction["inputs"]:
        inp_address = inp["address"][0][""]
        if inp_address in nodes:
            for output in transaction["outputs"]:
                output_address = output["address"]
                if output_address:
                    output_address = output_address[0][""]
                    if output_address in nodes:
                        edge = (inp_address, output_address)
                        if edge not in edges:
                            edges.append(edge)
G.add_nodes_from(nodes)
G.add_edges_from(edges)
