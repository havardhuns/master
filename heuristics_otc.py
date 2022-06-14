import os
from time import sleep
import graphsense
import pymongo
from dotenv import load_dotenv
from graphsense.api import addresses_api, bulk_api, txs_api, entities_api
from tqdm import tqdm

load_dotenv('.env')

api_key = os.environ.get("api_key")
configuration = graphsense.Configuration(host="https://api.graphsense.info")
configuration.api_key["api_key"] = api_key

api_client = graphsense.ApiClient(configuration)

addresses_api = addresses_api.AddressesApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)
txs_api = txs_api.TxsApi(api_client)
entities_api = entities_api.EntitiesApi(api_client)

connectURI = os.environ["connectURI"]
client = pymongo.MongoClient(connectURI)
db = client["master"]

def is_coin_generation(transaction):
    return transaction['coinbase']

def has_two_outputs(transaction):
    return len(transaction["outputs"]) == 2

def has_two_inputs(transaction):
    return len(transaction["inputs"]) == 2

def get_addresses(puts, json=False):
    addresses = []
    for put in puts:
        try:
            if json:
                addresses.append(put["address"][0][""])
            else:
                addresses.append(put["address"][0])
        except IndexError as e:
            continue
    return addresses

def has_self_change_address(transaction):
    input_addresses = get_addresses(transaction["inputs"])
    output_addresses = get_addresses(transaction["outputs"])
    for output_address in output_addresses:
        if output_address in input_addresses:
            return True
    return False

def get_first_transaction_hash(address):
    return addresses_api.get_address('btc', address)["first_tx"]["tx_hash"]

def get_latest_output_transaction_binary_search(transactions, low, high):
    if high >= low:
        mid = (high + low) // 2
        if transactions[mid].value.value > 0 and transactions[mid-1].value.value < 0:
            return transactions[mid]["tx_hash"]
        elif transactions[mid].value.value > 0:
            return get_latest_output_transaction_binary_search( transactions, low, mid - 1)
        else:
            return get_latest_output_transaction_binary_search( transactions, mid+1, high)
    else:
        return False

def is_used_as_output_later(address, current_transaction_tx_hash):
    response = addresses_api.list_address_txs(
        'btc', address, pagesize=500)
    if response["address_txs"][0]["tx_hash"] == current_transaction_tx_hash:
        return False
    while response:
        transactions = response["address_txs"]
        if transactions[-1].value.value > 0:
            return get_latest_output_transaction_binary_search( transactions, 0, len(transactions)-1) != current_transaction_tx_hash
        response = addresses_api.list_address_txs('btc', address, page=response['next_page'], pagesize=500)

def value_has_more_than_four_digits_after_dot(value):
    value = '{0:.8f}'.format(value * 10**(-8)).strip("0")
    number_of_decimals = len(value.split(".")[1])
    return number_of_decimals > 4

def otc_value_is_smaller_than_all_input_values(otc_value, inputs):
    input_values = [inp["value"]["value"] for inp in inputs]
    for input_value in input_values:
        if input_value < otc_value:
            return False
    return True

def has_not_been_otc_addressed_previously_h2_3(address):
    first_transaction_for_address_hash = get_first_transaction_hash(address)
    transaction_data = txs_api.get_tx('btc', first_transaction_for_address_hash, include_io=True)
    transaction = {"tx_hash": transaction_data["tx_hash"], "coinbase": transaction_data["coinbase"], "outputs": transaction_data["outputs"].value, "inputs": transaction_data["inputs"].value}

    if transaction['coinbase']:
        return True
    
    if not has_two_outputs(transaction):
        return True

    if has_two_inputs(transaction):
        return True

    otc_output = [output for output in transaction["outputs"] if output["address"][0] == address][0]
    other_output =  [output for output in transaction["outputs"] if output["address"][0] != address][0]

    if not value_has_more_than_four_digits_after_dot( otc_output["value"]["value"]):
        return True

    if has_self_change_address(transaction):
        return True

    first_transaction_for_other_address_hash = get_first_transaction_hash(other_output["address"][0])
    return transaction["tx_hash"] == first_transaction_for_other_address_hash

def has_not_been_otc_addressed_previously_h2_4(address):
    first_transaction_for_address_hash = get_first_transaction_hash(address)
    transaction_data = txs_api.get_tx('btc', first_transaction_for_address_hash, include_io=True)
    transaction = {"tx_hash": transaction_data["tx_hash"], "coinbase": transaction_data["coinbase"], "outputs": transaction_data["outputs"].value, "inputs": transaction_data["inputs"].value}

    if is_coin_generation(transaction):
        return True

    if has_self_change_address(transaction):
        return True
    
    if not has_two_outputs(transaction):
        return True

    if has_two_inputs(transaction):
        return True

    otc_output = [output for output in transaction["outputs"] if output["address"][0] == address][0]
    if not otc_value_is_smaller_than_all_input_values( otc_output["value"]["value"], transaction["inputs"]):
        return True

    other_output =  [output for output in transaction["outputs"] if output["address"][0] != address][0]
    first_transaction_for_other_address_hash = get_first_transaction_hash(other_output["address"][0])

    if transaction["tx_hash"] != first_transaction_for_other_address_hash:
        return False
    return not is_used_as_output_later(other_output["address"][0], transaction['tx_hash']) or is_used_as_output_later(address, transaction['tx_hash'])

def h2_123(transaction):
    otc_data = {
        "tx_hash": transaction["tx_hash"],
        "block_height": transaction["height"],
        "otc_output": None,
        "other_output": None,
        "heuristics": {
            "1": False,
            "2": False,
            "3": False
        }
    }

    # (2) The transaction T is not a coin generation;
    if is_coin_generation(transaction):
        return otc_data

    # (4) The transaction T has exactly two outputs. 
    if not has_two_outputs(transaction):
        return otc_data

    # (3) There is no address among the outputs that also appears in the inputs (self-change address); 
    if has_self_change_address(transaction):
        return otc_data

    # (1) This is the first appearance of the OTC address;
    output_1 = transaction["outputs"][0]
    output_2 = transaction["outputs"][1]
    output_address_1_first_transaction = get_first_transaction_hash(output_1["address"][0])
    output_address_2_first_transaction = get_first_transaction_hash(output_2["address"][0])

    is_first_transaction_of_output_address_1 = output_address_1_first_transaction == transaction['tx_hash']
    is_first_transaction_of_output_address_2 = output_address_2_first_transaction == transaction['tx_hash']

    if is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == False:
        return otc_data

    # (H2.2 (5)) Only the other output address is reused as an output address in some later transaction
    elif is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == True:
        output_1_used_later = is_used_as_output_later(output_1["address"][0], transaction["tx_hash"])
        output_2_used_later = is_used_as_output_later(output_2["address"][0], transaction["tx_hash"])
        if output_1_used_later != output_2_used_later:
            if output_1_used_later:
                otc_data["otc_output"] = output_2
                otc_data["other_output"] = output_1
                otc_data["heuristics"]["2"] = True
            elif output_2_used_later:
                otc_data["otc_output"] = output_1
                otc_data["other_output"] = output_2
                otc_data["heuristics"]["2"] = True

    # (H2.1 (5) and H2.3 (5)) This is not the first appearance of the other output address          
    else:
        if is_first_transaction_of_output_address_1:
            otc_data["otc_output"] = output_1
            otc_data["other_output"] = output_2
            otc_data["heuristics"]["1"] = True
        elif is_first_transaction_of_output_address_2:
            otc_data["otc_output"] = output_2
            otc_data["other_output"] = output_1
            otc_data["heuristics"]["1"] = True
        
        if is_used_as_output_later( otc_data["other_output"]["address"][0], transaction["tx_hash"]) and not is_used_as_output_later( otc_data["otc_output"]["address"][0], transaction["tx_hash"]):
            otc_data["heuristics"]["2"] = True

        # (H2.3 (6)) The number of inputs in transaction T is not equal to two.
        if has_two_inputs(transaction):
            return otc_data
    
        # (H2.3 (8)) Decimal representation of the value for the OTC address has more than 4 digits after the dot.
        if not value_has_more_than_four_digits_after_dot( otc_data["otc_output"]["value"]["value"]):
            return otc_data
    
        # (H2.3 (7)) ~O has not been OTC addressed in previous transactions
        if has_not_been_otc_addressed_previously_h2_3( otc_data["other_output"]["address"][0]):
            otc_data["heuristics"]["3"] = True
    return otc_data

def h2_4(transaction):
    otc_data = {
        "tx_hash": transaction["tx_hash"],
        "block_height": transaction["height"],
        "otc_output": None,
        "other_output": None,
        "heuristics": {
            "4": False
        }
    }

    # (2) The transaction T is not a coin generation;
    if is_coin_generation(transaction):
        return otc_data

    # (4) The transaction T has exactly two outputs. 
    if not has_two_outputs(transaction):
        return otc_data

    # (3) There is no address among the outputs that also appears in the inputs (self-change address); 
    if has_self_change_address(transaction):
        return otc_data

    output_1 = transaction["outputs"][0]
    output_2 = transaction["outputs"][1]

    is_first_transaction_of_output_address_1 = get_first_transaction_hash(output_1["address"][0]) == transaction['tx_hash']
    is_first_transaction_of_output_address_2 = get_first_transaction_hash(output_2["address"][0]) == transaction['tx_hash']

   # (1) This is the first appearance of the OTC address;
    if is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == False:
        return otc_data
    
    # (5) This is not the first appearance of the other output address OR only the other output address is reused as an output address in some later transaction
    elif is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == True:
        output_1_used_later = is_used_as_output_later(output_1["address"][0], transaction["tx_hash"])
        output_2_used_later = is_used_as_output_later(output_2["address"][0], transaction["tx_hash"])
        if output_1_used_later == output_2_used_later:
            return otc_data
        else:
            if output_1_used_later:
                otc_output = output_2
                other_output = output_1
            elif output_2_used_later:
                otc_output = output_1
                other_output = output_2
    else:
        if is_first_transaction_of_output_address_1:
            otc_output = output_1
            other_output = output_2
        elif is_first_transaction_of_output_address_2:
            otc_output = output_2
            other_output = output_1

        # (6) The other output address has not been OTC addressed in previous transactions
        if not has_not_been_otc_addressed_previously_h2_4( other_output["address"][0]):
            return otc_data
            
    # (7) The one time change value is smaller than any of the inputs
    if not otc_value_is_smaller_than_all_input_values( otc_output["value"]["value"], transaction["inputs"]):
        return otc_data
    
    otc_data["otc_output"] = otc_output
    otc_data["other_output"] = other_output
    otc_data["heuristics"]["4"] = True

    return otc_data


def run_otc_heuristic(heuristic_function, transactions_collection, otc_collection):
    transactions = transactions_collection.find({})
    transactions = [transaction for transaction in transactions]
    for transaction in tqdm(transactions):
        if otc_collection.count_documents({"tx_hash": transaction["tx_hash"]}) == 0:
            try:
                otc_data = heuristic_function(transaction)
            except graphsense.ApiException as e:
                print("Exception when calling Graphsense API, tx_hash:", transaction["tx_hash"],
                    e.status, e.reason)
                continue
            except IndexError as e:
                print("\nException - probably empty address array, tx_hash:", transaction["tx_hash"])
                continue
            otc_collection.insert_one(otc_data)

def otc_4():
    aggregated_transaction_collection = db['otc-addresses-data-set-1-with-height']
    proposed_otc_collection = db['data-set-1-otc-h-24']
    data_set_collection = db['data-set-1']

    aggregated_transactions = aggregated_transaction_collection.find({"$or": [{"heuristics.1": True}, {"heuristics.2": True}]}).sort("block_height", -1)
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
            proposed_otc["7"] = otc_value_is_smaller_than_all_input_values(aggregated_transaction["otc_output"]["value"]["value"], transaction["inputs"])
            proposed_otc["8"] = len(transaction["inputs"]) != 2
            proposed_otc["9"] = value_has_more_than_four_digits_after_dot(aggregated_transaction["otc_output"]["value"]["value"])
            proposed_otc_collection.insert_one(proposed_otc)

if __name__ == '__main__':
    otc_4()
    #run_otc_heuristic(h2_123, db['data-set-1'], db['otc-addresses-data-set-1'])
    #run_otc_heuristic(h2_4, db['data-set-2'], db['otc-addresses-data-set-2'])