import os
import pymongo
from dotenv import load_dotenv
from time import time
import matplotlib.pyplot as plt

load_dotenv('../.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
block_transactions_collection = db["data-set-1"]
aggregated_transactions_collection = db["aggregated-transactions_new"]

number_of_transactions = block_transactions_collection.count_documents({})

transactions = [0,0,0,0,0,0,0]
i = 0
while i < 7:
    height = (i+1)*100000
    transactions[i] = block_transactions_collection.count_documents({"height": {"$gt": height - 50000, "$lt": height+50000}})
    i+=1

labels = ["~100k", "~200k", "~300k", "~400k", "~500k", "~600k", "~700k"]
fig, ax = plt.subplots()
width = 0.35
ax.bar(labels, transactions, width)
ax.set_ylabel('Number of transactions')
ax.set_xlabel('Block')

plt.legend()
plt.grid(axis = 'y')
plt.show()