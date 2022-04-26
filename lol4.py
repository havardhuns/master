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

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['block-transactions']

transactions = collection.find()

occurences_inputs = [0,0,0,0,0]
occurences_outputs = [0,0,0,0,0]


for transaction in tqdm(transactions):
    number_of_inputs = len(transaction["inputs"])
    if number_of_inputs < 5:
        occurences_inputs[number_of_inputs-1] += 1
    else:
        occurences_inputs[4] += 1

    number_of_outputs = len(transaction["outputs"])
    if number_of_outputs < 5:
        occurences_outputs[number_of_outputs-1] += 1
    else:
        occurences_outputs[4] += 1

def sum_lists(first, second):
    return [x + y for x, y in zip(first, second)]

labels = ["1", "2", "3", "4", "5+"]

plt.bar(labels, occurences_inputs, color=['blue', 'red', 'blue', 'blue', 'blue'])
plt.title("Number of inputs in transactions")
plt.grid(axis = 'y')
plt.savefig('graphs/input_occurence.png')
plt.close()

plt.bar(labels, occurences_outputs, color=['red', 'blue', 'red', 'red', 'red'])
plt.title("Number of outputs in transactions")
plt.grid(axis = 'y')
plt.savefig('graphs/output_occurence.png')
plt.close()