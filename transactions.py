import json
import graphsense
from graphsense.api import addresses_api, entities_api, blocks_api, bulk_api
import matplotlib.pyplot as plt
from statistics import mode
from datetime import datetime
from tqdm import tqdm
from time import sleep, time

transactionsFile = open("transactions.json", "a+")

api_key = "i/cM9eSFHOvISa17naCYeo/g6qFCweoN"
configuration = graphsense.Configuration(host = "https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
blocks_api = blocks_api.BlocksApi(api_client)
bulk_call_api = bulk_api.BulkApi(api_client)

currency = "btc"
block_height = 500000

calls = 1
seconds = time()
time_limit = 60*60
max_calls = 900
buffer = 5*60

block_transactions = blocks_api.list_block_txs(currency, block_height)

addresses = []
transactions = []

for transaction in block_transactions:
    for inp in transaction.inputs.value:
        len(inp.address) > 0 and inp.address[0] not in addresses and addresses.append(inp.address[0])
    for outp in transaction.outputs.value:
        len(outp.address) > 0 and outp.address[0] not in addresses and addresses.append(outp.address[0])

print("Retreived", len(addresses), "from block with height", block_height)
print("Getting all transactions addresses have been involved in")

for address in tqdm(addresses):
    elapsed_time = time() - seconds
    calls += 2

    if calls > max_calls:
        print("number of transactions:", len(transactions))
        if elapsed_time > time_limit:
            print("resetting counters")
            seconds = 0
            calls = 0
        else:
            sleepTime = time_limit - elapsed_time + buffer
            print("sleeping for", sleepTime/60, "minutes")
            sleep(sleepTime)
            print("resetting counters")
            seconds = 0
            calls = 0

    address_transactions = addresses_api.list_address_txs('btc', address)
    address_transactions_hashes = [address_transaction.tx_hash for address_transaction in address_transactions.address_txs]
    body = {"tx_hash": address_transactions_hashes }

    api_response = bulk_call_api.bulk_json('btc', 'get_tx', 1, body)
    transactions += api_response
    with open("transactions.json", "w") as outfile:
        outfile.write(json.dumps(transactions))