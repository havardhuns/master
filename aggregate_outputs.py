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
collection = db['block-transactions']
aggregated_transactions = db["aggregated-transactions"]


transactions = collection.find({})

def get_entity_from_inputs_outputs(puts):
    for put in puts:
        entity = addresses_api.get_address_entity('btc', put["address"][0])
        if entity:
            return {"entity": entity["entity"], "no_addresses": entity["no_addresses"]}

def get_first_transaction_hash(address):
    return addresses_api.get_address('btc', address)["first_tx"]["tx_hash"]


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

def get_output_value(output):
    value = output["value"] * 10**(-8)
    return value

def is_used_as_output_later(address, current_transaction_tx_hash):
    response = addresses_api.list_address_txs(
        'btc', address, pagesize=100)
    if response["address_txs"][0]["tx_hash"] == current_transaction_tx_hash:
        return False
    while response:
        sleep(5)
        tx_hashes = [transaction["tx_hash"] for transaction in response["address_txs"]]
        current_transaction_in_transactions = current_transaction_tx_hash in tx_hashes
        if current_transaction_in_transactions:
            current_transaction_index = get_index_of_tx_hash(current_transaction_tx_hash, response["address_txs"])
            tx_hashes = tx_hashes[:current_transaction_index]
        body = {
                "tx_hash": tx_hashes, "io": "outputs"}
        try:
            outputs = bulk_api.bulk_json(
                'btc', 'get_tx_io', 1, body)
        except graphsense.ApiException as e:
            if (e.status == 429):
                sleep(int(e.headers["Retry-After"]) + 60)
                outputs = bulk_api.bulk_json(
                'btc', 'get_tx_io', 1, body)
            else:
                raise e
        if address in get_addresses(outputs, json=True):
            return True
        if current_transaction_in_transactions:
            return False
        response = addresses_api.list_address_txs('btc', address, page=response['next_page'], pagesize=1000)
    

def has_self_change_address(inputs, outputs):
    input_addresses = get_addresses(inputs)
    output_addresses = get_addresses(outputs)
    for value in input_addresses:
        if value in output_addresses:
            return True
    return False

def value_has_more_than_four_decimals(output):
    value = output["value"]["value"] * 10**(-8)
    number_of_decimals = len(str(value).split(".")[1])
    return number_of_decimals > 4

def get_index_of_tx_hash(tx_hash, transactions):
    for i, transaction in enumerate(transactions):
        if transaction["tx_hash"] == tx_hash:
            return i
    return False

def find_change_address(transaction):
    change_address = {
        "otc_output": None,
        "other_output": None,
        "heuristics": {
            "1": False,
            "2": False,
            "3": False
        },
        "entity": None
    }


    # (2) The transaction t has exactly two outputs. 
    if len(transaction['outputs']) != 2:
        return change_address

    # (1) The transaction t is not coin generation;
    if transaction['coinbase']:
        return change_address

    # (7) There is no address among the outputgs that also appears in the inputs (self-change address); 
    if has_self_change_address(transaction['inputs'], transaction['outputs']):
        return change_address

    # (4) This is the first appearance of address O;
    # (5) This is not the first appearance of address ~O
    output_1 = transaction["outputs"][0]
    output_2 = transaction["outputs"][1]
    output_address_1_first_transaction = get_first_transaction_hash(output_1["address"][0])
    output_address_2_first_transaction = get_first_transaction_hash(output_2["address"][0])

    is_first_transaction_of_output_address_1 = output_address_1_first_transaction == transaction['tx_hash']
    is_first_transaction_of_output_address_2 = output_address_2_first_transaction == transaction['tx_hash']

    # (4) This is the first appearance of address O;
    if is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == False:
        return change_address
    
    # (4) This is the first appearance of address O;
    if is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2 == True:
        output_1_used_later = is_used_as_output_later(output_1["address"][0], transaction["tx_hash"])
        output_2_used_later = is_used_as_output_later(output_2["address"][0], transaction["tx_hash"])
        if not output_1_used_later == output_2_used_later:
            if output_1_used_later:
                change_address["otc_output"] = output_2
                change_address["other_output"] = output_1
                change_address["heuristics"]["2"] = True
            elif output_2_used_later:
                change_address["otc_output"] = output_1
                change_address["other_output"] = output_2
                change_address["heuristics"]["2"] = True
    # (5) This is not the first appearance of address ~O
    else:
        if is_first_transaction_of_output_address_1:
            change_address["otc_output"] = output_1
            change_address["other_output"] = output_2
            change_address["heuristics"]["1"] = True
        elif is_first_transaction_of_output_address_2:
            change_address["otc_output"] = output_2
            change_address["other_output"] = output_1
            change_address["heuristics"]["1"] = True
        
        if is_used_as_output_later(change_address["other_output"]["address"][0], transaction["tx_hash"]):
            change_address["heuristics"]["2"] = True

        # (3) The number of t inputs is not equal to two.
        if len(transaction['inputs']) == 2:
            return change_address
    
        # (6) Decimal representation of the value for address O has more than 4 digits after the dot.
        if not value_has_more_than_four_decimals(change_address["otc_output"]):
            return change_address
    
        # (9) ~O has not been OTC addressed in previous transactions
        if not has_been_otc_addressed_previously(change_address["other_output"]["address"][0]):
            change_address["heuristics"]["3"] = True
    return change_address

def has_been_otc_addressed_previously(otc_address_candidate):
    first_transaction_for_address_hash = get_first_transaction_hash(otc_address_candidate)
    transaction = txs_api.get_tx('btc', first_transaction_for_address_hash, include_io=True)
    outputs = transaction["outputs"].value
    inputs = transaction["inputs"].value
    # (4) This is the first appearance of address O;
    if otc_address_candidate not in get_addresses(outputs):
        return False

    # (1) The transaction t is not coin generation;
    if transaction['coinbase']:
        return False
    
    # (2) The transaction t has exactly two outputs. 
    if len(outputs) != 2:
        return False

    # (3) The number of t inputs is not equal to two.
    if len(outputs) == 2:
        return False

    otc_output = [output for output in outputs if output["address"][0] == otc_address_candidate][0]
    other_output =  [output for output in outputs if output["address"][0] != otc_address_candidate][0]

    # (6) Decimal representation of the value for address O has more than 4 digits after the dot.
    if not value_has_more_than_four_decimals(otc_output):
        return False

    # (7) There is no address among the outputs that also appears in the inputs (self-change address); 
    if has_self_change_address(inputs, outputs):
        return False

    # (5) This is not the first appearance of address ~O
    first_transaction_for_other_address_hash = get_first_transaction_hash(other_output["address"][0])
    if transaction["tx_hash"] == first_transaction_for_other_address_hash:
        return False

    '''# (8) Address ~O is reused as output addresses in some later transactions.
    index_of_transaction = get_index_of_tx_hash(transaction["tx_hash"], other_transactions)
    if not is_used_as_output_later(other_output["address"][0], other_transactions, transaction["tx_hash"]):
        continue'''
    return True

#todo
def find_change_address_strict(transaction):
    change_address = {
            "_id": transaction["tx_hash"],
            "tx_hash": transaction["tx_hash"],
            "otc_output": None,
            "other_output": None,
        }
    
    # (1) The transaction t is not a coin generation. 
    if transaction['coinbase']:
        return None

    # (2) The transaction t has exactly two outputs. 
    if len(transaction['outputs']) != 2:
        return None

    # (3) The number of t inputs is not equal to two.
    if len(transaction['inputs']) == 2:
            return None
    
    # (4) There is no address among the outputs that also appears in the inputs (self-change address); 
    if has_self_change_address(transaction['inputs'], transaction['outputs']):
        return False

    # (5) This is the first appearance of address O
    # (6) This is not the first appearance of address ~O
    output_1 = transaction["outputs"][0]
    output_2 = transaction["outputs"][1]
    output_address_1_first_transaction = get_first_transaction_hash(output_1["address"][0])
    output_address_2_first_transaction = get_first_transaction_hash(output_2["address"][0])

    is_first_transaction_of_output_address_1 = output_address_1_first_transaction == transaction['tx_hash']
    is_first_transaction_of_output_address_2 = output_address_2_first_transaction == transaction['tx_hash']

    if is_first_transaction_of_output_address_1 == is_first_transaction_of_output_address_2:
        return False

    if is_first_transaction_of_output_address_1:
            change_address["otc_output"] = output_1
            change_address["other_output"] = output_2
    elif is_first_transaction_of_output_address_2:
        change_address["otc_output"] = output_2
        change_address["other_output"] = output_1
    
    # (7) Decimal representation of the value for address O has more than 4 digits after the dot.
        if not value_has_more_than_four_decimals(change_address["otc_output"]):
            return None

    # (8) Address ~O is reused as output addresses in some later transactions.
    if not is_used_as_output_later(change_address["other_output"]["address"][0], transaction["tx_hash"]):
        return False

    # (9) ~O has not been OTC addressed in previous transactions
    if has_been_otc_addressed_previously(change_address["other_output"]["address"][0]):
        return False

    return change_address


for transaction in tqdm(transactions):
    count = aggregated_transactions.count_documents({"tx_hash": transaction["tx_hash"]})
    if count == 0:
        aggregated_transaction = {"_id": transaction["_id"], "tx_hash": transaction["tx_hash"]}
        try:  
            input_entity = get_entity_from_inputs_outputs(transaction["inputs"])
            aggregated_transaction["aggregated_inputs"] = {"entity": input_entity}
            sleep(1)
            aggregated_transaction["aggregated_outputs"] = find_change_address(transaction)
            if aggregated_transaction["aggregated_outputs"]["otc_output"]:
                aggregated_transaction["aggregated_outputs"]["entity"] = get_entity_from_inputs_outputs([aggregated_transaction["aggregated_outputs"]["otc_output"]])
            else:
                aggregated_transaction["aggregated_outputs"] = None
        except graphsense.ApiException as e:
            print("Exception when calling AddressesApi->list_address_txs:",
                e.status, e.reason)
            continue
        except IndexError as e:
            print("\nException, probably empty address array. tx_hash:", transaction["tx_hash"])
            continue
        aggregated_transactions.insert_one(aggregated_transaction)