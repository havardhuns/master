import pymongo

#connectURI = "mongodb://havardhuns:pwd@10.212.136.61/master?retryWrites=true&w=majority"
connectURI = "mongodb://havardhuns:pwd@localhost/master?retryWrites=true&w=majority"

client = pymongo.MongoClient(connectURI)
db = client["master"]
test_collection = db["test"]

test_collection.insert_one({"test": "Funker"})

print(test_collection.find_one_and_delete({"test": {'$exists': True}})['test'])
