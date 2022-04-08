''' WIP '''

import os
from time import sleep
import graphsense
from dotenv import load_dotenv
from graphsense.api import addresses_api, bulk_api
from tqdm import tqdm

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)

def getAllTransactionsForAddress(address):
    address_transactions = []
    response = addresses_api.list_address_txs(
        'btc', address, pagesize=1000)
    address_transactions.extend(response.address_txs)
    while 'next_page' in response:
        response = addresses_api.list_address_txs(
            'btc', address, page=response['next_page'], pagesize=1000)
        address_transactions.extend(response.address_txs)
    print(address_transactions == list(reversed(sorted(address_transactions, key = lambda k: k['timestamp']))))
    return address_transactions

def get_inputs(tx_hashes):
    io_list = []
    i = 0
    while i < len(tx_hashes):
        try:
            body = {
                "tx_hash": tx_hashes[i:i+50], "io": "inputs"}
            io_list.extend(bulk_api.bulk_json(
                'btc', 'get_tx_io', 1, body, async_req=True).get())
        except graphsense.ApiException as e:
            if (e.status == 429):
                sleep(int(e.headers["Retry-After"]) + 60)
                continue
            else:
                raise e
        sleep(3)
        i += 50
    return io_list

def get_input_addresses(inputs):
    input_addresses = []
    for put in inputs:
        if "_info" in put and put["_info"] == "no data":
            continue
        address = []
        try:
            address = [put["address"][0][""]]
        except IndexError:
            continue
        if address not in input_addresses:
            input_addresses.append(address)
    return input_addresses


def aggregateInputs(address):
    address_transactions = getAllTransactionsForAddress(address)
    address_transactions_hashes = [
        address_transaction["tx_hash"] for address_transaction in address_transactions["address_txs"]]
    inputs = get_inputs(address_transactions_hashes)
    input_addresses = get_input_addresses(inputs)
    return input_addresses