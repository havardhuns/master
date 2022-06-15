import os
import pymongo
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv('.env')


connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]


def format_h_123():
    transactions_collection = db['data-set-1']
    aggregated_transactions_collection = db["otc-addresses-data-set-1_backup"]
    aggregated_transactions_new = db["otc-addresses-data-set-1-with-height"]

    aggregated_transactions = aggregated_transactions_collection.find()
    for aggregated_transaction in tqdm(aggregated_transactions):
        if aggregated_transactions_new.count_documents({"_id" : aggregated_transaction["_id"]}) == 0:
            transaction = transactions_collection.find_one({"tx_hash": aggregated_transaction["tx_hash"]})
            is_otc = aggregated_transaction["aggregated_outputs"] is not None
            otc_output = aggregated_transaction["aggregated_outputs"]["otc_output"] if is_otc else None
            other_output = aggregated_transaction["aggregated_outputs"]["other_output"] if is_otc else None
            heuristics = aggregated_transaction["aggregated_outputs"]["heuristics"] if is_otc else {"1": False, "2": False, "3": False}
            new_document = {"tx_hash": aggregated_transaction["tx_hash"], "block_height": transaction["height"], "otc_output": otc_output, "other_output": other_output, "heuristics": heuristics} 
            aggregated_transactions_new.insert_one(new_document)


def format_h_4():
    transactions_collection = db['data-set-2']
    aggregated_transactions_collection = db["otc-outputs-new_copy"]
    aggregated_transactions_new = db["otc-addresses-data-set-2"]
    aggregated_transactions = aggregated_transactions_collection.find()
    aggregated_transactions = [aggregated_transaction for aggregated_transaction in aggregated_transactions]
    for aggregated_transaction in tqdm(aggregated_transactions):
        if aggregated_transactions_new.count_documents({"_id" : aggregated_transaction["_id"]}) == 0:
            transaction = transactions_collection.find_one({"tx_hash": aggregated_transaction["tx_hash"]})
            is_otc = aggregated_transaction["aggregated_outputs"] is not None
            otc_output = aggregated_transaction["aggregated_outputs"]["otc_output"] if is_otc else None
            other_output = aggregated_transaction["aggregated_outputs"]["other_output"] if is_otc else None
            heuristics = {"4": True} if is_otc else {"4" : False}
            new_document = {"tx_hash": aggregated_transaction["tx_hash"], "block_height": transaction["height"], "otc_output": otc_output, "other_output": other_output, "heuristics": heuristics} 
            aggregated_transactions_new.insert_one(new_document)
format_h_4()