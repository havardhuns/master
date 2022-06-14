import networkx as nx
import pymongo
from tqdm import tqdm
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib_venn import venn2



'''
Creates graphs visualizing how many inputs are in transactions
'''

load_dotenv('../.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
collection = db['block-transactions']

transactions = collection.find()

occurences_inputs = [0,0,0,0,0]
occurences_outputs = [0,0,0,0,0]

total_number_of_inputs = 0
total_number_of_transactions = collection.count_documents({})

venn = [0,0,0]


for transaction in tqdm(transactions):
    number_of_inputs = len(transaction["inputs"])
    total_number_of_inputs += number_of_inputs
    if number_of_inputs < 5:
        occurences_inputs[number_of_inputs-1] += 1
    else:
        occurences_inputs[4] += 1

    number_of_outputs = len(transaction["outputs"])
    if number_of_outputs < 5:
        occurences_outputs[number_of_outputs-1] += 1
    else:
        occurences_outputs[4] += 1
    if number_of_inputs > 1:
        venn[0] += 1
    if number_of_outputs == 1:
        venn[1] += 1
    if number_of_inputs >1 and number_of_outputs == 1:
        venn[2] +=1

def sum_lists(first, second):
    return [x + y for x, y in zip(first, second)]

labels = ["1", "2", "3", "4", "5+"]

print(occurences_outputs)


plt.bar(labels, occurences_inputs, color=['green', 'red', 'green', 'green', 'green'], edgecolor = 'black')
plt.title("Number of inputs in transactions")
plt.xlabel("Number of inputs")
plt.ylabel("Number of transactions")
plt.grid(axis = 'y')
plt.savefig('graphs/input_occurence.png')
plt.close()

plt.bar(labels, occurences_outputs, color=['green', 'red', 'red', 'red', 'red'], edgecolor = 'black')
plt.title("Number of outputs in transactions")
plt.xlabel("Number of outputs")
plt.ylabel("Number of transactions")
plt.grid(axis = 'y')
plt.savefig('graphs/output_occurence.png')
plt.close()

venn2(subsets = tuple(venn), set_labels = ('Multiple inputs', 'One output'))
plt.show()

print("total number of inputs")
print(total_number_of_inputs)
print("average")
print(total_number_of_inputs / total_number_of_transactions) 