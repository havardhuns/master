import json
import os
from datetime import datetime
from statistics import mode
from time import sleep, time

import graphsense
import matplotlib.pyplot as plt
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, blocks_api, bulk_api, entities_api
from tqdm import tqdm

load_dotenv('.env')

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
transactions_collection = db["transactions"]
addresses_collection = db["addresses"]

# empty collections
#transactions_collection.delete_many({})
#addresses_collection.delete_many({})

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
blocks_api = blocks_api.BlocksApi(api_client)
bulk_call_api = bulk_api.BulkApi(api_client)

currency = "btc"
block_height = 500000


block_transactions = blocks_api.list_block_txs(currency, block_height)

addresses = []

for transaction in block_transactions:
    for inp in transaction.inputs.value:
        len(inp.address) > 0 and inp.address[0] not in addresses and addresses.append(
            inp.address[0])
    for outp in transaction.outputs.value:
        len(outp.address) > 0 and outp.address[0] not in addresses and addresses.append(
            outp.address[0])

print("Retreived", len(addresses), " addresses from block with height", block_height)
print("Getting all transactions addresses have been involved in")

for address in tqdm(addresses):
    count = addresses_collection.count_documents({"_id" : address})
    if count == 0:
        try:
            # get all transactions for address
            address_transactions = addresses_api.list_address_txs('btc', address)
        except graphsense.ApiException as e:
            print("Exception when calling AddressesApi->list_address_txs:",
                e.status, e.reason)
            continue

        address_transactions_hashes = [
            address_transaction.tx_hash for address_transaction in address_transactions.address_txs]
        detailed_transactions_list = []
        i = 0
        while i < len(address_transactions_hashes):
            try:
                # get detailed data for all the transactions for address
                body = {"tx_hash": address_transactions_hashes[i:i+50], "include_io": True}
                detailed_transactions_list.extend(bulk_call_api.bulk_json('btc', 'get_tx', 1, body, async_req= True).get())
            except graphsense.ApiException as e:
                if (e.status == 429):
                    sleep(int(e.headers["Retry-After"]) + 60)
                else:
                    print("Exception when calling bulk api->get_tx:", e.status, e.reason)
                continue
            i += 50
        #insert in database
        if detailed_transactions_list:
            for transaction in detailed_transactions_list:
                transaction.update( {"_id": transaction['tx_hash']})
            addresses_collection.insert_one({"_id": address})
            try:
                transactions_collection.insert_many(detailed_transactions_list, ordered=False)
            except pymongo.errors.BulkWriteError as e:
                #amount_of_transactions = len(detailed_transactions_list)
                #inserted = e.details["nInserted"]
                #print("Insterted", inserted, "transactions.", amount_of_transactions -  inserted, "already in db")
                continue
    if count > 1:
        print("Duplicate addresses:", address)
