import requests
import os
import graphsense
from dotenv import load_dotenv
from graphsense.api import blocks_api, general_api
import datetime
from tqdm import tqdm

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)
blocks_api = blocks_api.BlocksApi(api_client)
general_api = general_api.GeneralApi(api_client)


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


def get_block_timestamp(height):
    try:
        api_response = blocks_api.get_block('btc', height)
        return api_response['timestamp']
    except graphsense.ApiException as e:
        print("Exception when calling BlocksApi->get_block: %s\n" % e)


def get_transactions_in_time_interval(start_date, end_date):
    graphsense_statistics = general_api.get_statistics()
    latest_block_height = [statistic['no_blocks'] - 1
                           for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]

    start_block = find_block_by_timestamp_binary_search(
        0, latest_block_height, start_date, True)
    end_block = find_block_by_timestamp_binary_search(
        start_block, latest_block_height, end_date, False)

    transactions = []
    for block_height in tqdm(range(start_block, end_block+1)):
        block_transactions = blocks_api.list_block_txs('btc', block_height)
        transactions.extend(block_transactions)
    return transactions


start_date = datetime.datetime(2022, 2, 28).timestamp()
end_date = datetime.datetime(2022, 2, 28).timestamp() + 3600

print(len(get_transactions_in_time_interval(start_date, end_date)))
