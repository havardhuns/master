import pymongo
import os
from dotenv import load_dotenv
from tqdm import tqdm

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

def has_self_change_address(inputs, outputs):
    input_addresses = get_addresses(inputs)
    output_addresses = get_addresses(outputs)
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
        if inputs:
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
    transactions_common_input = cursor_to_list(transactions_collection.find({ "outputs": { "$size": 1}}))
    common_input_address_clustering(transactions_common_input, entities_collection)

    #Find transactions with more than one output and crate individual clusters for each address
    transactions_individual_input = cursor_to_list(transactions_collection.find({ "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 1]}}))
    individual_input_address_clustering(transactions_individual_input, entities_collection)


def h1_3(transactions_collection, entities_collection, otc_collection):
    #Find all transactions with one output
    transactions_common_input = cursor_to_list(transactions_collection.find({ "outputs": { "$size": 1}}))

    #Find all transactions with more than two outputs
    transactions_individual_input = cursor_to_list(transactions_collection.find({ "$expr" : { "$gt" : [{ "$size" : "$outputs" } , 2]}}))

    #Find transactions with two outputs and check for change address from otc_collection
    transactions_two_outputs = cursor_to_list(transactions_collection.find({ "outputs": { "$size": 2}}))
    for transaction in transactions_two_outputs:
        if has_self_change_address(transaction) or otc_collection.find_one({"$and": [{"tx_hash": transaction["tx_hash"]}, {"heuristics.4": True}]}):
            transactions_common_input.append(transaction)
        else:
            transactions_individual_input.append(transaction)

    common_input_address_clustering(transactions_common_input, entities_collection)
    individual_input_address_clustering(transactions_individual_input, entities_collection)



transactions_collection = db['data-set-2']
entities_collection = db['entities-data-set-2']
otc_collection = db['otc-addresses-data-set-2']

h1_3(transactions_collection, entities_collection, otc_collection)