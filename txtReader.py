import os
from dotenv import load_dotenv
import graphsense
from graphsense.api import addresses_api

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)


'''f = open('sdnlist.txt').read().split("\n\n")[2:]

lol = []

for paragraph in f:
    if "XBT" in paragraph:
        lol.append(paragraph)

addresses = []
count = 0

for fml in lol:
    rip = fml.split('XBT')[1:]
    for faen in rip:
        addresses.append(faen.split(";")[0].strip().split(" ")[0])

for address in addresses[25]:
    try:
        # get all transactions for address
        address_transactions = addresses_api.list_address_txs(
            'btc', address)
    except graphsense.ApiException as e:
        print("Exception when calling AddressesApi->list_address_txs:",
              e.status, e.reason)
        continue
    print(len(address_transactions.address_txs))
    count += len(address_transactions.address_txs)

print(count)
'''

address = "1NE2NiGhhbkFPSEyNWwj7hKGhGDedBtSrQ"
address_transactions = addresses_api.list_address_txs(
    'btc', address)
print(address_transactions)
