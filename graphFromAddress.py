import graphsense
import pymongo
from graphsense.api import addresses_api, entities_api, blocks_api, bulk_api
import matplotlib.pyplot as plt
from tqdm import tqdm
import networkx as nx

level = 2
address = "3NWBZKC9UZ6fYRDMwLDAM6hoD1mkT5WgAS"
G = nx.DiGraph()

api_key = "i/cM9eSFHOvISa17naCYeo/g6qFCweoN"
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
bulk_call_api = bulk_api.BulkApi(api_client)


def getAllTransactionsForAnAddress(address):
    try:
        # get all transactions for address
        address_transactions = addresses_api.list_address_txs('btc', address)
    except graphsense.ApiException as e:
        print("Exception when calling AddressesApi->list_address_txs:",
              e.status, e.reason)
        return False
    address_transactions = addresses_api.list_address_txs('btc', address)
    address_transactions_hashes = [
        address_transaction.tx_hash for address_transaction in address_transactions.address_txs]

    detailed_transactions_list = []
    i = 0
    while i < len(address_transactions_hashes):
        try:
            # get detailed data for all the transactions for address
            body = {
                "tx_hash": address_transactions_hashes[i:i+50], "include_io": True}
            detailed_transactions_list.extend(bulk_call_api.bulk_json(
                'btc', 'get_tx', 1, body, async_req=True).get())
        except graphsense.ApiException as e:
            if (e.status == 429):
                sleep(int(e.headers["Retry-After"]) + 60)
            else:
                print("Exception when calling bulk api->get_tx:",
                      e.status, e.reason)
            continue
        i += 50
    return detailed_transactions_list


detailed_transactions_list = getAllTransactionsForAnAddress(address)
addresses = [address]
for transaction in detailed_transactions_list:
    for inp in transaction["inputs"]:
        inp_address = inp["address"][0][""]
        if inp_address not in addresses:
            addresses.append(inp_address)
    for output in transaction["outputs"]:
        output_address = output["address"][0][""]
        if output_address not in addresses:
            addresses.append(output_address)
addresses.remove(address)

for address in tqdm(addresses):
    detailed_transactions_list.extend(getAllTransactionsForAnAddress(address))

edges = []
nodes = []

for transaction in detailed_transactions_list:
    for inp in transaction["inputs"]:
        inp_address = inp["address"][0][""]
        if inp_address not in nodes:
            nodes.append(inp_address)
        for output in transaction["outputs"]:
            output_address = output["address"][0][""]
            if output_address not in nodes:
                nodes.append(output_address)
            edge = (inp_address, output_address)
            if edge not in edges:
                edges.append(edge)
G.add_nodes_from(nodes)
G.add_edges_from(edges)

color_map = []
for node in G:
    if node == address:
        color_map.append('red')
    else:
        color_map.append('blue')
nx.draw(G, node_color=color_map)
plt.show()
