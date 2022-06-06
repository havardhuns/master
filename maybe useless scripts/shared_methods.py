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

def has_self_change_address(inputs, outputs):
    input_addresses = get_addresses(inputs)
    output_addresses = get_addresses(outputs)
    for value in input_addresses:
        if value in output_addresses:
            return True
    return False

def get_entity_from_inputs_outputs(puts):
    for put in puts:
        entity = addresses_api.get_address_entity('btc', put["address"][0])
        if entity:
            return {"entity": entity["entity"], "no_addresses": entity["no_addresses"]}

def otc_4():
    aggregated_transactions = aggregated_transactions.find({}).sort("height", -1)
    aggregated_transactions = [x for x in aggregated_transactions]
    for aggregated_transaction in tqdm(aggregated_transactions):
        if aggregated_transaction["aggregated_outputs"]:
            if aggregated_transaction["aggregated_outputs"]["heuristics"]["1"] or aggregated_transaction["aggregated_outputs"]["heuristics"]["2"]:
                count = proposed_otc_collection.count_documents({"tx_hash" : aggregated_transaction["tx_hash"]})
                if count == 0:
                    transaction = data_set_1.find_one({"tx_hash" : aggregated_transaction["tx_hash"]})
                    proposed_otc = {"_id": aggregated_transaction["tx_hash"], "tx_hash": aggregated_transaction["tx_hash"], "6": False, "7": False, "8": False}
                    proposed_otc["6"] = len(transaction["inputs"]) != 2
                    try:
                        proposed_otc["7"] = has_not_been_otc_addressed_previously_h2_4(aggregated_transaction["aggregated_outputs"]["other_output"]["address"][0])
                    except graphsense.ApiException as e:
                        proposed_otc["7"] = None
                    proposed_otc["8"] = otc_value_is_smaller_than_inputs(aggregated_transaction["aggregated_outputs"]["otc_output"]["value"]["value"], transaction["inputs"])
                    proposed_otc_collection.insert_one(proposed_otc)