import os
import graphsense
from dotenv import load_dotenv
from graphsense.api import blocks_api, general_api, bulk_api, txs_api
import datetime
from tqdm import tqdm
from time import sleep
import pymongo

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key
connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]
time_transactions = db["time-transactions"]
block_transactions = db["new-time-transactions"]

api_client = graphsense.ApiClient(configuration)

blocks_api = blocks_api.BlocksApi(api_client)
general_api = general_api.GeneralApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)
txs_api = txs_api.TxsApi(api_client)



def find_block_by_timestamp_binary_search(low, high, timestamp, roundUp):
    if high >= low:
        mid = (high + low) // 2
        mid_timestamp = get_block_timestamp(mid)
        if mid_timestamp == timestamp:
            return mid
        elif mid_timestamp > timestamp:
            return find_block_by_timestamp_binary_search(low, mid - 1, timestamp, roundUp)
        else:
            return find_block_by_timestamp_binary_search(mid + 1, high, timestamp, roundUp)
    else:
        if roundUp:
            return low
        else:
            return high

def get_number_of_transactions_in_block(block_height):
    return blocks_api.get_block('btc', block_height)["no_txs"]


def get_block_timestamp(block_height):
    try:
        api_response = blocks_api.get_block('btc', block_height)
        return api_response['timestamp']
    except graphsense.ApiException as e:
        print("Exception when calling BlocksApi->get_block: %s\n" % e)

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

def formatValue(value):
    return {"value": int(value["value"]), "fiat_values": [{"code": fv["code"], "value": fv["value"]} for fv in value["fiat_values"]]}
    


def format_transactions(transactions, inputs, outputs):
    formatted_transactions = []
    inputs = format_input_output(inputs)
    outputs = format_input_output(outputs)
    for transaction in transactions:
        fortmatted_transaction = {"_id": transaction["tx_hash"], "coinbase": transaction["coinbase"], "height": None, "inputs": [], "outputs": [], "timestamp": transaction["timestamp"], "total_input": {}, "total_output": {}, "tx_hash": transaction["tx_hash"], "tx_type": transaction["tx_type"]}
        fortmatted_transaction["height"] = transaction["height"]["value"]
        fortmatted_transaction["total_input"] = formatValue(transaction["total_input"])
        fortmatted_transaction["total_output"] = formatValue(transaction["total_output"])
        fortmatted_transaction["inputs"] = [{i:inp[i] for i in inp if i!='_request_tx_hash'} for inp in inputs if inp["_request_tx_hash"] == transaction["tx_hash"]]
        fortmatted_transaction["outputs"] = [{i:output[i] for i in output if i!='_request_tx_hash'} for output in outputs if output["_request_tx_hash"] == transaction["tx_hash"]]
        formatted_transactions.append(fortmatted_transaction)
    return formatted_transactions

def get_blocks(block_height, number_of_transactions):
    current_number_of_transactions = 0
    current_block_height = block_height
    blocks = []
    increment = 1
    while current_number_of_transactions < number_of_transactions:
        current_number_of_transactions += get_number_of_transactions_in_block(current_block_height)
        blocks.append(current_block_height)
        current_block_height = block_height + increment
        if increment > 0:
            increment = -increment
        else:
            increment = -(increment - 1)
    return sorted(blocks)

def get_detailed_transaciton_info_alternative(tx_hashes):
    transactions = []
    for tx_hash in tx_hashes:
        try:
            transactions.append(txs_api.get_tx("btc", tx_hash, include_io=True))
        except graphsense.ApiException as e:
            print("exception")
            continue
       


def get_transactions_from_blocks(block_list):
    for block_height in tqdm(block_list):
        count = block_transactions.count_documents({"height": block_height})
        if count == 0:
            transactions = blocks_api.list_block_txs('btc', block_height)
            tx_hashes = [transaction["tx_hash"] for transaction in transactions]
            try:
                inputs = get_io(tx_hashes, "inputs")
                outputs = get_io(tx_hashes, "outputs")
                block_transactions.insert_many(format_transactions(transactions, inputs, outputs))
            except graphsense.ApiException as e:
                if e.status == 502:
                    print("alternative")
                    formatted_transactions = get_detailed_transaciton_info_alternative(tx_hashes)
                    for transaction in formatted_transactions:
                        transaction.update({"_id": transaction['tx_hash']})
                        block_transactions.insert_many(formatted_transactions)
                else:
                    print("Exception:",
                    e.status, e.reason)
                    continue

def get_transactions_in_time_interval(start_date, end_date):
    graphsense_statistics = general_api.get_statistics()
    latest_block_height = [statistic['no_blocks'] - 1
                           for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]
    print(latest_block_height)
    start_block = find_block_by_timestamp_binary_search(
        0, latest_block_height, start_date, True)
    end_block = find_block_by_timestamp_binary_search(
        start_block, latest_block_height, end_date, False)
    return (start_block, end_block)

start_date = datetime.datetime(2022, 2, 1).timestamp()
end_date = datetime.datetime(2022, 2, 3).timestamp()

start_block, end_block = get_transactions_in_time_interval(start_date, end_date)
print(start_block)
print(end_block)
get_transactions_from_blocks(list(range(start_block, end_block+1)))


'''graphsense_statistics = general_api.get_statistics()
latest_block_height = [statistic['no_blocks'] - 1
                        for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]'''

'''for block_height in range(200000, latest_block_height, 100000):
    print("getting transactions from block", block_height)
    get_transactions_from_blocks(get_blocks(block_height, 10000))'''

'''print(get_blocks(700000, 10000))'''
