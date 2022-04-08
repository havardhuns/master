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
collection = db['transactions-block-500']
addresses = db['addresses']

transactions = collection.find({"coinbase": False})

occurences_1_2_3plus = [0] * 3
occurrences_3_to_20 = [0] * 18
occurrences_21_to_210 = [0] * 190
occurrences_211_to_max = [0]


for transaction in tqdm(transactions):
    number_of_inputs = len(transaction["inputs"])
    if number_of_inputs == 1:
        occurences_1_2_3plus[0] += 1
    elif number_of_inputs == 2:
        occurences_1_2_3plus[1] += 1
    elif number_of_inputs > 2:
        occurences_1_2_3plus[2] += 1
        if number_of_inputs <= 20:
            occurrences_3_to_20[number_of_inputs - 3] += 1
        elif number_of_inputs <= 210:
            occurrences_21_to_210[number_of_inputs - 21] += 1
        else:
            if len(occurrences_211_to_max) < number_of_inputs - 210:
                occurrences_211_to_max.extend(
                    [0] * (number_of_inputs - 210 - len(occurrences_211_to_max)))
            occurrences_211_to_max[number_of_inputs - 211] += 1

plt.bar(["1", "2", "3+"], occurences_1_2_3plus)
plt.title("Number of inputs in transactions")
plt.savefig('graphs/occurences_1_2_3plus.png')
plt.close()

plt.plot(range(3, 21), occurrences_3_to_20)
plt.xticks(range(3, 21))
plt.title("Transactions with 3 to 20 inputs")
plt.savefig('graphs/occurrences_3_to_20.png')
plt.close()

plt.plot(range(21, 211), occurrences_21_to_210)
plt.title("Transactions with 21 to 210 inputs")
plt.savefig('graphs/occurrences_21_to_210.png')
plt.close()

plt.plot(range(211, len(occurrences_211_to_max) + 211), occurrences_211_to_max)
plt.title("Transactions with more than 210 inputs")
plt.savefig('graphs/occurrences_211_to_max.png')
plt.close()
