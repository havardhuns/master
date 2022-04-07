import networkx as nx
import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt


'''
Creates graphs visualizing how many inputs are in transactions
'''

load_dotenv('.env')

address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
level = 2
G = nx.DiGraph()

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['linked-inputs-test']
collection2 = db['unique-inputs']
transactions = db['transactions']

addresses = collection.find()
addresses2 = collection2.find()

min_value = 3
max_value = 10
occurences = [0] * (max_value - min_value + 1)

for address in tqdm(addresses):
    number_of_addresses = len(address["addresses"])
    if min_value <= number_of_addresses <= max_value:
        occurences[number_of_addresses - min_value] += 1

'''occurences2 = [0] * (max_value - min_value + 1)
for address in tqdm(addresses2):
    number_of_addresses = len(address["addresses"])
    if min_value <= number_of_addresses <= max_value:
        occurences2[number_of_addresses - min_value] += 1'''

plt.plot(range(min_value, max_value+1), occurences,
         label="number of addresses an entity has")
#plt.plot(range(min_value, max_value+1), occurences2, label="unique inputs in transactions, number of addresses")
plt.xticks(range(min_value, max_value+1))
plt.yticks(range(0, occurences[0], 500))
plt.grid(True)
plt.title("Aggregated inputs")
leg = plt.legend()
plt.show()
