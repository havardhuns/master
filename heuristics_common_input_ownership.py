import pymongo
import os
from dotenv import load_dotenv
from tqdm import tqdm
from time import sleep

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

def get_addresses(puts):
    addresses = []
    for put in puts:
        try:
            addresses.append(put["address"][0])
        except IndexError as e:
            continue
    return addresses

def has_self_change_address(transaction):
    input_addresses = get_addresses(transaction["inputs"])
    output_addresses = get_addresses(transaction["outputs"])
    for output_address in output_addresses:
        if output_address in input_addresses:
            return True
    return False

def common_input_address_clustering(transactions, entities_collection):
    for transaction in tqdm(transactions):
        inputs = get_addresses(transaction["inputs"])
        existing_entity = False
        for address in inputs:
            #Try to find entity with address in cluster
            entity_with_shared_input_address = entities_collection.find_one({"address_cluster": address})
            if entity_with_shared_input_address:
                existing_entity = True
                entities_collection.update_one({
                    '_id': entity_with_shared_input_address['_id']
                }, {
                    '$addToSet': {
                        'address_cluster': { '$each': inputs}
                    },
                    '$push': {
                        'tx_hashes': transaction["tx_hash"]
                    }
                })
                break
        if not existing_entity:
            entities_collection.insert_one(
                {"address_cluster": inputs, "tx_hashes": [transaction["tx_hash"]]})
            entities_collection.create_index("address_cluster")

def individual_input_address_clustering(transactions, entities_collection):
    for transaction in tqdm(transactions):
        inputs = get_addresses(transaction["inputs"])
        for address in inputs:
            if not entities_collection.find_one({"address_cluster": address}):
                entities_collection.insert_one(
                    {"address_cluster": [address], "tx_hashes": [transaction["tx_hash"]]})
                entities_collection.create_index("address_cluster")

def cursor_to_list(cursor):
    return [item for item in cursor]

def h1_1(transactions_collection, entities_collection):
    transactions_common_input = cursor_to_list(transactions_collection.find({"coinbase": False}))
    common_input_address_clustering(transactions_common_input, entities_collection)

def h1_2(transactions_collection, entities_collection):
    #Find all transactions with one output, and cluster the inputs
    transactions_common_input = cursor_to_list(transactions_collection.find({"$and": [{"coinbase": False}, { "outputs": { "$size": 1}}]}))
    common_input_address_clustering(transactions_common_input, entities_collection)

    #Find transactions with more than one output and crate individual clusters for each address
    transactions_individual_input = cursor_to_list(transactions_collection.find({"$and": [{"coinbase": False}, { "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 1]}}]}))
    individual_input_address_clustering(transactions_individual_input, entities_collection)


def h1_3(transactions_collection, entities_collection, otc_collection):
    #Find all transactions with one output
    transactions_common_input = cursor_to_list(transactions_collection.find({ "outputs": { "$size": 1}}))

    #Find all transactions with more than two outputs
    transactions_individual_input = cursor_to_list(transactions_collection.find(({"$and": [{"coinbase": False}, { "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 2]}}]})))

    #Find transactions with two outputs and check for change address from otc_collection
    transactions_two_outputs = cursor_to_list(transactions_collection.find({ "outputs": { "$size": 2}}))
    for transaction in transactions_two_outputs:
        if has_self_change_address(transaction) or otc_collection.find_one({"$and": [{"tx_hash": transaction["tx_hash"]}, {"heuristics.4": True}]}):
            transactions_common_input.append(transaction)
        else:
            transactions_individual_input.append(transaction)

    common_input_address_clustering(transactions_common_input, entities_collection)
    individual_input_address_clustering(transactions_individual_input, entities_collection)

def h1_1_d1():
    for block_height in range(100000, 700001, 100000):
            transactions_collection = db["data-set-1"]
            transactions_common_input = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, {"coinbase": False}]}))
            entities_collection = db[f'z-linked-inputs-{block_height}-1']
            common_input_address_clustering(transactions_common_input, entities_collection)

def h1_2_d1():
    for block_height in range(100000, 700001, 100000):
            transactions_collection = db["data-set-1"]
            transactions_common_input = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, {"coinbase": False}, { "outputs": { "$size": 1}}]}))
            entities_collection = db[f'z-linked-inputs-{block_height}-2']
            common_input_address_clustering(transactions_common_input, entities_collection)

            transactions_individual_input = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, {"coinbase": False}, { "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 1]}}]}))
            individual_input_address_clustering(transactions_individual_input, entities_collection)

def h1_3_d1():
    for block_height in range(100000, 700001, 100000):
            transactions_collection = db["data-set-1"]
            transactions_common_input = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, { "outputs": { "$size": 1}}]}))
            entities_collection = db[f'z-linked-inputs-{block_height}-3']
            otc_collection = db['data-set-1-otc-h-24']
            
            transactions_individual_input = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, { "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 2]}}]}))

            transactions_two_outputs = cursor_to_list(transactions_collection.find({"$and": [{"height": {"$gt": block_height-50000, "$lt": block_height+50000}}, { "outputs": { "$size": 2}}]}))
            for transaction in transactions_two_outputs:
                if has_self_change_address(transaction) or otc_collection.find_one({"$and": [{"tx_hash": transaction["tx_hash"]}, {"6": True}, {"7": True}]}):
                    transactions_common_input.append(transaction)
                else:
                    transactions_individual_input.append(transaction)
            common_input_address_clustering(transactions_common_input, entities_collection)
            individual_input_address_clustering(transactions_individual_input, entities_collection)
            
def deletedb():
    for i in range(100000, 700001, 100000):
        for j in range(1,4):
            collection = db[f'z-linked-inputs-{i}-{j}']
            collection.drop()

#h1_1_d1()
#h1_2_d1()
#h1_3_d1()


def h1_1_d2():
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    print(number_of_transactions)
    for i in range(0, number_of_transactions, 10000):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        transactions = data_set_2.find({}).sort([("height", 1), ("_id", 1)]).skip(i).limit(10000).allow_disk_use(True)
        transactions = cursor_to_list(transactions)
        entity_collection = db[f'z-z-1-entity-{i}-{i+increment-1}-1']
        if i != 0:
            old_entity_collection = db[f'z-z-1-entity-{i-10000}-{i-1}-1']
            entity_collection.insert_many(old_entity_collection.find({}))
            sleep(30)
        common_input_address_clustering(transactions, entity_collection)

def h1_3_d2():
    data_set_2 = db['data-set-2']
    otc_collection = db['otc-addresses-data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    print(number_of_transactions)
    for i in range(0, number_of_transactions, 10000):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        transactions = data_set_2.find({}).sort([("height", 1), ("_id", 1)]).skip(i).limit(10000).allow_disk_use(True)
        transactions = cursor_to_list(transactions)
        entity_collection = db[f'z-z-2-entity-{i}-{i+increment-1}-2']
        if i!= 0:
            old_entity_collection = db[f'z-z-2-entity-{i-10000}-{i-1}-2']
            entity_collection.insert_many(old_entity_collection.find({}))
            sleep(30)


        transactions_common = []
        transaction_uniqiue = []
        for transaction in transactions:
            if len(transaction["outputs"]) == 1:
                transactions_common.append(transaction)
            elif len(transaction["outputs"]) == 2:
                if has_self_change_address(transaction) or otc_collection.find_one({"$and": [{"tx_hash": transaction["tx_hash"]}, {"heuristics.4": True}]}):
                    transactions_common.append(transaction)
                else:
                    transaction_uniqiue.append(transaction)
            else:
                transaction_uniqiue.append(transaction)
        common_input_address_clustering(transactions_common, entity_collection)
        individual_input_address_clustering(transaction_uniqiue, entity_collection)


def deletedb_2(number):
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in range(0, number_of_transactions, 10000):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        entity_db = db[f'z-z-entity-{i}-{i+increment-1}-{number}']
        entity_db.drop()
    
def print_no_entities(number):
    data_set_2 = db['data-set-2']
    number_of_transactions = data_set_2.count_documents({})
    for i in range(0, number_of_transactions, 10000):
        increment = 10000 if number_of_transactions -i > 10000 else number_of_transactions-i+1
        entity_db = db[f'z-z-{number}-entity-{i}-{i+increment-1}-{number}']
        print(entity_db.count_documents({}))

#deletedb_2()
#deletedb_2()

#h1_1_d2()
#h1_3_d2()

print_no_entities(1)

'''transactions_collection = db['data-set-2']
entities_collection = db['entities-data-set-2']
otc_collection = db['otc-addresses-data-set-2']

h1_3(transactions_collection, entities_collection, otc_collection)'''
