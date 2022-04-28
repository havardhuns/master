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

def get_inputs(inputs, json=False):
    addresses = []
    for inp in inputs:
        try:
            addresses.append(inp["address"][0])
        except IndexError as e:
            continue
    return addresses

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