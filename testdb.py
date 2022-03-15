import os
import pymongo
from dotenv import load_dotenv

'''
test if you can connect to database
'''

load_dotenv(".env")
connectURI = os.environ.get("connectURI")

client = pymongo.MongoClient(connectURI)
db = client["master"]
test_collection = db["test"]

test_collection.insert_one({"test": "Funker"})

print(test_collection.find_one_and_delete({"test": {'$exists': True}})['test'])
