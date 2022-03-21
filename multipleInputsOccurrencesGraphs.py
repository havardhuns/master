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
collection = db['transactions']
addresses = db['addresses']
addresses_collection = db[f'nodes-{address}']

transactions = collection.find({"coinbase": False})

occurences_1_2_3plus = [0] * 3
occurrences_3_to_19 = [0] * 17
occurrences_20_to_99 = [0] * 80
occurrences_100_to_max = [0]


for transaction in tqdm(transactions):
    number_of_inputs = len(transaction["inputs"])
    if number_of_inputs == 1:
        occurences_1_2_3plus[0] += 1
    elif number_of_inputs == 2:
        occurences_1_2_3plus[1] += 1
    elif number_of_inputs > 2:
        occurences_1_2_3plus[2] += 1
        if number_of_inputs < 20:
            occurrences_3_to_19[number_of_inputs - 3] += 1
        elif number_of_inputs < 100:
            occurrences_20_to_99[number_of_inputs - 20] += 1
        else:
            if len(occurrences_100_to_max) < number_of_inputs - 99:
                occurrences_100_to_max.extend(
                    [0] * (number_of_inputs - 99 - len(occurrences_100_to_max)))
            occurrences_100_to_max[number_of_inputs - 100] += 1

plt.bar(["1", "2", "3+"], occurences_1_2_3plus)
plt.title("Number of inputs in transactions")
plt.savefig('graphs/occurences_1_2_3plus.png')
plt.close()

plt.plot(range(3, 20), occurrences_3_to_19)
plt.xticks(range(3, 20))
plt.title("Transactions with 3 to 19 inputs")
plt.savefig('graphs/occurrences_3_to_19.png')
plt.close()

plt.plot(range(20, 100), occurrences_20_to_99)
plt.title("Transactions with 20 to 99 inputs")
plt.savefig('graphs/occurrences_20_to_99.png')
plt.close()

plt.plot(range(100, len(occurrences_100_to_max) + 100), occurrences_100_to_max)
plt.title("Transactions with 100 inputs or more")
plt.savefig('graphs/occurrences_100_to_max.png')
plt.close()
