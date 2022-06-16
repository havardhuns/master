import os
import pymongo
from dotenv import load_dotenv
from tqdm import tqdm
import graphsense
from heuristics_otc import has_not_been_otc_addressed_previously_h2_4, otc_value_is_smaller_than_all_input_values, value_has_more_than_four_digits_after_dot

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

def otc_4_d1():
    aggregated_transaction_collection = db['otc-addresses-data-set-1-with-height']
    proposed_otc_collection = db['data-set-1-otc-h-24']
    data_set_collection = db['data-set-1']

    aggregated_transactions = aggregated_transaction_collection.find({"$or": [{"heuristics.1": True}, {"heuristics.2": True}]}).sort("block_height", -1).sort("block_height", 1)
    aggregated_transactions = [x for x in aggregated_transactions]
    for aggregated_transaction in tqdm(aggregated_transactions):
        count = proposed_otc_collection.count_documents({"tx_hash" : aggregated_transaction["tx_hash"]})
        if count == 0:
            transaction = data_set_collection.find_one({"tx_hash" : aggregated_transaction["tx_hash"]})
            proposed_otc = {"tx_hash": aggregated_transaction["tx_hash"], "block_height": aggregated_transaction["block_height"], "6": False, "7": False, "8": False, "9": False}
            try:
                proposed_otc["6"] = has_not_been_otc_addressed_previously_h2_4(aggregated_transaction["other_output"]["address"][0])
            except graphsense.ApiException as e:
                proposed_otc["6"] = None
            except IndexError:
                proposed_otc["6"] = None
            proposed_otc["7"] = otc_value_is_smaller_than_all_input_values(aggregated_transaction["otc_output"]["value"]["value"], transaction["inputs"])
            proposed_otc["8"] = len(transaction["inputs"]) != 2
            proposed_otc["9"] = value_has_more_than_four_digits_after_dot(aggregated_transaction["otc_output"]["value"]["value"])
            proposed_otc_collection.insert_one(proposed_otc)

otc_4_d1()