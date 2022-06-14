import os
import graphsense
from dotenv import load_dotenv
from graphsense.api import blocks_api, general_api, bulk_api
import datetime
from time import sleep
import pymongo
from tqdm import tqdm

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key
connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)

db = client["master"]

api_client = graphsense.ApiClient(configuration)
blocks_api = blocks_api.BlocksApi(api_client)
general_api = general_api.GeneralApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)

def get_io(tx_hashes, io):
    io_list = []
    i = 0
    while i < len(tx_hashes):
        try:
            body = {
                "tx_hash": tx_hashes[i:i+50], "io": io}
            io_list.extend(bulk_api.bulk_json(
                'btc', 'get_tx_io', 1, body, async_req=True).get())
        except graphsense.ApiException as e:
            # Request limit exceeded
            if (e.status == 429):
                sleep(int(e.headers["Retry-After"]) + 60)
                continue
            else:
                raise e
        i += 50
    return io_list

def format_input_output(puts):
    formatted_puts = []
    for put in puts:
        if "_info" in put and put["_info"] == "no data":
            continue
        address = []
        try:
            address = [put["address"][0][""]]
        except IndexError:
            pass
        formatted_puts.append({"_request_tx_hash": put["_request_tx_hash"], "address": address, "value": {"fiat_values" : [{"code": "eur", "value": put["value_eur"]}, {"code": "usd", "value": put["value_usd"]}], "value": int(put["value_value"])}})
    return formatted_puts

def format_value(value):
    return {"value": int(value["value"]), "fiat_values": [{"code": fv["code"], "value": fv["value"]} for fv in value["fiat_values"]]}

def format_transactions(transactions, inputs, outputs):
    formatted_transactions = []
    inputs = format_input_output(inputs)
    outputs = format_input_output(outputs)
    for transaction in transactions:
        fortmatted_transaction = {"_id": transaction["tx_hash"], "coinbase": transaction["coinbase"], "height": None, "inputs": [], "outputs": [], "timestamp": transaction["timestamp"], "total_input": {}, "total_output": {}, "tx_hash": transaction["tx_hash"], "tx_type": transaction["tx_type"]}
        fortmatted_transaction["height"] = transaction["height"]["value"]
        fortmatted_transaction["total_input"] = format_value(transaction["total_input"])
        fortmatted_transaction["total_output"] = format_value(transaction["total_output"])
        fortmatted_transaction["inputs"] = [{i:inp[i] for i in inp if i!='_request_tx_hash'} for inp in inputs if inp["_request_tx_hash"] == transaction["tx_hash"]]
        fortmatted_transaction["outputs"] = [{i:output[i] for i in output if i!='_request_tx_hash'} for output in outputs if output["_request_tx_hash"] == transaction["tx_hash"]]
        formatted_transactions.append(fortmatted_transaction)
    return formatted_transactions

def get_transactions_from_block_with_io(block_height):
    transactions = blocks_api.list_block_txs('btc', block_height)
    tx_hashes = [transaction["tx_hash"] for transaction in transactions]
    inputs = get_io(tx_hashes, "inputs")
    outputs = get_io(tx_hashes, "outputs")
    return format_transactions(transactions, inputs, outputs)

def get_list_of_surrounding_blocks_for_number_of_transactions( block_height, number_of_transactions):
    current_number_of_transactions = 0
    current_block_height = block_height
    blocks = []
    increment = 1
    while current_number_of_transactions < number_of_transactions:
        blocks.append(current_block_height)
        number_of_transactions_in_block = blocks_api.get_block('btc', current_block_height)["no_txs"]
        current_number_of_transactions += number_of_transactions_in_block
        current_block_height = block_height + increment
        increment = -increment if increment > 0 else -increment + 1
    return sorted(blocks)

def find_block_by_timestamp_binary_search(min_block_height, max_block_height, timestamp, ensuing):
    if max_block_height >= min_block_height:
        mid_block_height = (max_block_height + min_block_height) // 2
        mid_block = blocks_api.get_block('btc', mid_block_height)
        if mid_block['timestamp'] == timestamp:
            return mid_block_height
        elif mid_block['timestamp'] > timestamp:
            return find_block_by_timestamp_binary_search(min_block_height, mid_block_height - 1, timestamp, ensuing)
        else:
            return find_block_by_timestamp_binary_search(mid_block_height + 1, max_block_height, timestamp, ensuing)
    else:
        if ensuing:
            return min_block_height
        else:
            return max_block_height

def create_data_set_1():
    data_set_1 = db['data-set-1']
    graphsense_statistics = general_api.get_statistics()
    latest_block_height = [statistic['no_blocks'] - 1 for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]
    for block_height in range(100000, latest_block_height, 100000):
        block_list = get_list_of_surrounding_blocks_for_number_of_transactions( block_height, 10000)
        for block_height in tqdm(block_list):
            if data_set_1.count_documents({"height": block_height}) == 0:
                try:
                    transactions = get_transactions_from_block_with_io(block_height)
                except graphsense.ApiException as e:
                    print("Exception when calling Graphsense API, block_height:", block_height,
                        e.status, e.reason)
                    continue
                data_set_1.insert_many(transactions)

def create_data_set_2():
    data_set_2 = db['data-set-2']
    graphsense_statistics = general_api.get_statistics()
    latest_block_height = [statistic['no_blocks'] - 1
                           for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]
    print(latest_block_height)
    start_date = datetime.datetime(2022, 2, 1).timestamp()
    end_date = datetime.datetime(2022, 2, 3).timestamp()
    start_block = find_block_by_timestamp_binary_search(
        0, latest_block_height, start_date, True)
    end_block = find_block_by_timestamp_binary_search(
        start_block, latest_block_height, end_date, False)
    block_list = list(range(start_block, end_block+1))
    for block_height in tqdm(block_list):
            if data_set_2.count_documents({"height": block_height}) == 0:
                try:
                    transactions = get_transactions_from_block_with_io(block_height)
                except graphsense.ApiException as e:
                    print("Exception when calling Graphsense API, block_height:", block_height,
                        e.status, e.reason)
                    continue
                data_set_2.insert_many(transactions)

