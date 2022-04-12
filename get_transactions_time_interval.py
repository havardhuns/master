import os
import graphsense
from dotenv import load_dotenv
from graphsense.api import blocks_api, general_api, bulk_api
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
block_transactions = db["block-transactions"]

api_client = graphsense.ApiClient(configuration)

blocks_api = blocks_api.BlocksApi(api_client)
general_api = general_api.GeneralApi(api_client)
bulk_api = bulk_api.BulkApi(api_client)



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
        sleep(3)
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
       


def get_transactions_from_blocks(block_list):
    for block_height in tqdm(block_list):
        count = block_transactions.count_documents({"height": block_height})
        if count == 0:
            try:
                transactions = blocks_api.list_block_txs('btc', block_height)
                tx_hashes = [transaction["tx_hash"] for transaction in block_transactions]
                inputs = get_io(tx_hashes, "inputs")
                outputs = get_io(tx_hashes, "outputs")
                block_transactions.insert_many(format_transactions(transactions, inputs, outputs))
            except graphsense.ApiException as e:
                print("Exception:",
                    e.status, e.reason)
                continue
            sleep(10)

def get_transactions_in_time_interval(start_date, end_date):
    graphsense_statistics = general_api.get_statistics()
    latest_block_height = [statistic['no_blocks'] - 1
                           for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]

    start_block = find_block_by_timestamp_binary_search(
        0, latest_block_height, start_date, True)
    end_block = find_block_by_timestamp_binary_search(
        start_block, latest_block_height, end_date, False)
    return (start_block, end_block)

start_date = datetime.datetime(2017, 12, 18).timestamp()
end_date = datetime.datetime(2017, 12, 18).timestamp() + 3600 * 24

'''
start_block, end_block = get_transactions_in_time_interval(start_date, end_date)
get_transactions_from_blocks(list(range(start_block, end_block+1)))
'''

hundretusen = [98827, 98828, 98829, 98830, 98831, 98832, 98833, 98834, 98835, 98836, 98837, 98838, 98839, 98840, 98841, 98842, 98843, 98844, 98845, 98846, 98847, 98848, 98849, 98850, 98851, 98852, 98853, 98854, 98855, 98856, 98857, 98858, 98859, 98860, 98861, 98862, 98863, 98864, 98865, 98866, 98867, 98868, 98869, 98870, 98871, 98872, 98873, 98874, 98875, 98876, 98877, 98878, 98879, 98880, 98881, 98882, 98883, 98884, 98885, 98886, 98887, 98888, 98889, 98890, 98891, 98892, 98893, 98894, 98895, 98896, 98897, 98898, 98899, 98900, 98901, 98902, 98903, 98904, 98905, 98906, 98907, 98908, 98909, 98910, 98911, 98912, 98913, 98914, 98915, 98916, 98917, 98918, 98919, 98920, 98921, 98922, 98923, 98924, 98925, 98926, 98927, 98928, 98929, 98930, 98931, 98932, 98933, 98934, 98935, 98936, 98937, 98938, 98939, 98940, 98941, 98942, 98943, 98944, 98945, 98946, 98947, 98948, 98949, 98950, 98951, 98952, 98953, 98954, 98955, 98956, 98957, 98958, 98959, 98960, 98961, 98962, 98963, 98964, 98965, 98966, 98967, 98968, 98969, 98970, 98971, 98972, 98973, 98974, 98975, 98976, 98977, 98978, 98979, 98980, 98981, 98982, 98983, 98984, 98985, 98986, 98987, 98988, 98989, 98990, 98991, 98992, 98993, 98994, 98995, 98996, 98997, 98998, 98999, 99000, 99001, 99002, 99003, 99004, 99005, 99006, 99007, 99008, 99009, 99010, 99011, 99012, 99013, 99014, 99015, 99016, 99017, 99018, 99019, 99020, 99021, 99022, 99023, 99024, 99025, 99026, 99027, 99028, 99029, 99030, 99031, 99032, 99033, 99034, 99035, 99036, 99037, 99038, 99039, 99040, 99041, 99042, 99043, 99044, 99045, 99046, 99047, 99048, 99049, 99050, 99051, 99052, 99053, 99054, 99055, 99056, 99057, 99058, 99059, 99060, 99061, 99062, 99063, 99064, 99065, 99066, 99067, 99068, 99069, 99070, 99071, 99072, 99073, 99074, 99075, 99076, 99077, 99078, 99079, 99080, 99081, 99082, 99083, 99084, 99085, 99086, 99087, 99088, 99089, 99090, 99091, 99092, 99093, 99094, 99095, 99096, 99097, 99098, 99099, 99100, 99101, 99102, 99103, 99104, 99105, 99106, 99107, 99108, 99109, 99110, 99111, 99112, 99113, 99114, 99115, 99116, 99117, 99118, 99119, 99120, 99121, 99122, 99123, 99124, 99125, 99126, 99127, 99128, 99129, 99130, 99131, 99132, 99133, 99134, 99135, 99136, 99137, 99138, 99139, 99140, 99141, 99142, 99143, 99144, 99145, 99146, 99147, 99148, 99149, 99150, 99151, 99152, 99153, 99154, 99155, 99156, 99157, 99158, 99159, 99160, 99161, 99162, 99163, 99164, 99165, 99166, 99167, 99168, 99169, 99170, 99171, 99172, 99173, 99174, 99175, 99176, 99177, 99178, 99179, 99180, 99181, 99182, 99183, 99184, 99185, 99186, 99187, 99188, 99189, 99190, 99191, 99192, 99193, 99194, 99195, 99196, 99197, 99198, 99199, 99200, 99201, 99202, 99203, 99204, 99205, 99206, 99207, 99208, 99209, 99210, 99211, 99212, 99213, 99214, 99215, 99216, 99217, 99218, 99219, 99220, 99221, 99222, 99223, 99224, 99225, 99226, 99227, 99228, 99229, 99230, 99231, 99232, 99233, 99234, 99235, 99236, 99237, 99238, 99239, 99240, 99241, 99242, 99243, 99244, 99245, 99246, 99247, 99248, 99249, 99250, 99251, 99252, 99253, 99254, 99255, 99256, 99257, 99258, 99259, 99260, 99261, 99262, 99263, 99264, 99265, 99266, 99267, 99268, 99269, 99270, 99271, 99272, 99273, 99274, 99275, 99276, 99277, 99278, 99279, 99280, 99281, 99282, 99283, 99284, 99285, 99286, 99287, 99288, 99289, 99290, 99291, 99292, 99293, 99294, 99295, 99296, 99297, 99298, 99299, 99300, 99301, 99302, 99303, 99304, 99305, 99306, 99307, 99308, 99309, 99310, 99311, 99312, 99313, 99314, 99315, 99316, 99317, 99318, 99319, 99320, 99321, 99322, 99323, 99324, 99325, 99326, 99327, 99328, 99329, 99330, 99331, 99332, 99333, 99334, 99335, 99336, 99337, 99338, 99339, 99340, 99341, 99342, 99343, 99344, 99345, 99346, 99347, 99348, 99349, 99350, 99351, 99352, 99353, 99354, 99355, 99356, 99357, 99358, 99359, 99360, 99361, 99362, 99363, 99364, 99365, 99366, 99367, 99368, 99369, 99370, 99371, 99372, 99373, 99374, 99375, 99376, 99377, 99378, 99379, 99380, 99381, 99382, 99383, 99384, 99385, 99386, 99387, 99388, 99389, 99390, 99391, 99392, 99393, 99394, 99395, 99396, 99397, 99398, 99399, 99400, 99401, 99402, 99403, 99404, 99405, 99406, 99407, 99408, 99409, 99410, 99411, 99412, 99413, 99414, 99415, 99416, 99417, 99418, 99419, 99420, 99421, 99422, 99423, 99424, 99425, 99426, 99427, 99428, 99429, 99430, 99431, 99432, 99433, 99434, 99435, 99436, 99437, 99438, 99439, 99440, 99441, 99442, 99443, 99444, 99445, 99446, 99447, 99448, 99449, 99450, 99451, 99452, 99453, 99454, 99455, 99456, 99457, 99458, 99459, 99460, 99461, 99462, 99463, 99464, 99465, 99466, 99467, 99468, 99469, 99470, 99471, 99472, 99473, 99474, 99475, 99476, 99477, 99478, 99479, 99480, 99481, 99482, 99483, 99484, 99485, 99486, 99487, 99488, 99489, 99490, 99491, 99492, 99493, 99494, 99495, 99496, 99497, 99498, 99499, 99500, 99501, 99502, 99503, 99504, 99505, 99506, 99507, 99508, 99509, 99510, 99511, 99512, 99513, 99514, 99515, 99516, 99517, 99518, 99519, 99520, 99521, 99522, 99523, 99524, 99525, 99526, 99527, 99528, 99529, 99530, 99531, 99532, 99533, 99534, 99535, 99536, 99537, 99538, 99539, 99540, 99541, 99542, 99543, 99544, 99545, 99546, 99547, 99548, 99549, 99550, 99551, 99552, 99553, 99554, 99555, 99556, 99557, 99558, 99559, 99560, 99561, 99562, 99563, 99564, 99565, 99566, 99567, 99568, 99569, 99570, 99571, 99572, 99573, 99574, 99575, 99576, 99577, 99578, 99579, 99580, 99581, 99582, 99583, 99584, 99585, 99586, 99587, 99588, 99589, 99590, 99591, 99592, 99593, 99594, 99595, 99596, 99597, 99598, 99599, 99600, 99601, 99602, 99603, 99604, 99605, 99606, 99607, 99608, 99609, 99610, 99611, 99612, 99613, 99614, 99615, 99616, 99617, 99618, 99619, 99620, 99621, 99622, 99623, 99624, 99625, 99626, 99627, 99628, 99629, 99630, 99631, 99632, 99633, 99634, 99635, 99636, 99637, 99638, 99639, 99640, 99641, 99642, 99643, 99644, 99645, 99646, 99647, 99648, 99649, 99650, 99651, 99652, 99653, 99654, 99655, 99656, 99657, 99658, 99659, 99660, 99661, 99662, 99663, 99664, 99665, 99666, 99667, 99668, 99669, 99670, 99671, 99672, 99673, 99674, 99675, 99676, 99677, 99678, 99679, 99680, 99681, 99682, 99683, 99684, 99685, 99686, 99687, 99688, 99689, 99690, 99691, 99692, 99693, 99694, 99695, 99696, 99697, 99698, 99699, 99700, 99701, 99702, 99703, 99704, 99705, 99706, 99707, 99708, 99709, 99710, 99711, 99712, 99713, 99714, 99715, 99716, 99717, 99718, 99719, 99720, 99721, 99722, 99723, 99724, 99725, 99726, 99727, 99728, 99729, 99730, 99731, 99732, 99733, 99734, 99735, 99736, 99737, 99738, 99739, 99740, 99741, 99742, 99743, 99744, 99745, 99746, 99747, 99748, 99749, 99750, 99751, 99752, 99753, 99754, 99755, 99756, 99757, 99758, 99759, 99760, 99761, 99762, 99763, 99764, 99765, 99766, 99767, 99768, 99769, 99770, 99771, 99772, 99773, 99774, 99775, 99776, 99777, 99778, 99779, 99780, 99781, 99782, 99783, 99784, 99785, 99786, 99787, 99788, 99789, 99790, 99791, 99792, 99793, 99794, 99795, 99796, 99797, 99798, 99799, 99800, 99801, 99802, 99803, 99804, 99805, 99806, 99807, 99808, 99809, 99810, 99811, 99812, 99813, 99814, 99815, 99816, 99817, 99818, 99819, 99820, 99821, 99822, 99823, 99824, 99825, 99826, 99827, 99828, 99829, 99830, 99831, 99832, 99833, 99834, 99835, 99836, 99837, 99838, 99839, 99840, 99841, 99842, 99843, 99844, 99845, 99846, 99847, 99848, 99849, 99850, 99851, 99852, 99853, 99854, 99855, 99856, 99857, 99858, 99859, 99860, 99861, 99862, 99863, 99864, 99865, 99866, 99867, 99868, 99869, 99870, 99871, 99872, 99873, 99874, 99875, 99876, 99877, 99878, 99879, 99880, 99881, 99882, 99883, 99884, 99885, 99886, 99887, 99888, 99889, 99890, 99891, 99892, 99893, 99894, 99895, 99896, 99897, 99898, 99899, 99900, 99901, 99902, 99903, 99904, 99905, 99906, 99907, 99908, 99909, 99910, 99911, 99912, 99913, 99914, 99915, 99916, 99917, 99918, 99919, 99920, 99921, 99922, 99923, 99924, 99925, 99926, 99927, 99928, 99929, 99930, 99931, 99932, 99933, 99934, 99935, 99936, 99937, 99938, 99939, 99940, 99941, 99942, 99943, 99944, 99945, 99946, 99947, 99948, 99949, 99950, 99951, 99952, 99953, 99954, 99955, 99956, 99957, 99958, 99959, 99960, 99961, 99962, 99963, 99964, 99965, 99966, 99967, 99968, 99969, 99970, 99971, 99972, 99973, 99974, 99975, 99976, 99977, 99978, 99979, 99980, 99981, 99982, 99983, 99984, 99985, 99986, 99987, 99988, 99989, 99990, 99991, 99992, 99993, 99994, 99995, 99996, 99997, 99998, 99999, 100000, 100001, 100002, 100003, 100004, 100005, 100006, 100007, 100008, 100009, 100010, 100011, 100012, 100013, 100014, 100015, 100016, 100017, 100018, 100019, 100020, 100021, 100022, 100023, 100024, 100025, 100026, 100027, 100028, 100029, 100030, 100031, 100032, 100033, 100034, 100035, 100036, 100037, 100038, 100039, 100040, 100041, 100042, 100043, 100044, 100045, 100046, 100047, 100048, 100049, 100050, 100051, 100052, 100053, 100054, 100055, 100056, 100057, 100058, 100059, 100060, 100061, 100062, 100063, 100064, 100065, 100066, 100067, 100068, 100069, 100070, 100071, 100072, 100073, 100074, 100075, 100076, 100077, 100078, 100079, 100080, 100081, 100082, 100083, 100084, 100085, 100086, 100087, 100088, 100089, 100090, 100091, 100092, 100093, 100094, 100095, 100096, 100097, 100098, 100099, 100100, 100101, 100102, 100103, 100104, 100105, 100106, 100107, 100108, 100109, 100110, 100111, 100112, 100113, 100114, 100115, 100116, 100117, 100118, 100119, 100120, 100121, 100122, 100123, 100124, 100125, 100126, 100127, 100128, 100129, 100130, 100131, 100132, 100133, 100134, 100135, 100136, 100137, 100138, 100139, 100140, 100141, 100142, 100143, 100144, 100145, 100146, 100147, 100148, 100149, 100150, 100151, 100152, 100153, 100154, 100155, 100156, 100157, 100158, 100159, 100160, 100161, 100162, 100163, 100164, 100165, 100166, 100167, 100168, 100169, 100170, 100171, 100172, 100173, 100174, 100175, 100176, 100177, 100178, 100179, 100180, 100181, 100182, 100183, 100184, 100185, 100186, 100187, 100188, 100189, 100190, 100191, 100192, 100193, 100194, 100195, 100196, 100197, 100198, 100199, 100200, 100201, 100202, 100203, 100204, 100205, 100206, 100207, 100208, 100209, 100210, 100211, 100212, 100213, 100214, 100215, 100216, 100217, 100218, 100219, 100220, 100221, 100222, 100223, 100224, 100225, 100226, 100227, 100228, 100229, 100230, 100231, 100232, 100233, 100234, 100235, 100236, 100237, 100238, 100239, 100240, 100241, 100242, 100243, 100244, 100245, 100246, 100247, 100248, 100249, 100250, 100251, 100252, 100253, 100254, 100255, 100256, 100257, 100258, 100259, 100260, 100261, 100262, 100263, 100264, 100265, 100266, 100267, 100268, 100269, 100270, 100271, 100272, 100273, 100274, 100275, 100276, 100277, 100278, 100279, 100280, 100281, 100282, 100283, 100284, 100285, 100286, 100287, 100288, 100289, 100290, 100291, 100292, 100293, 100294, 100295, 100296, 100297, 100298, 100299, 100300, 100301, 100302, 100303, 100304, 100305, 100306, 100307, 100308, 100309, 100310, 100311, 100312, 100313, 100314, 100315, 100316, 100317, 100318, 100319, 100320, 100321, 100322, 100323, 100324, 100325, 100326, 100327, 100328, 100329, 100330, 100331, 100332, 100333, 100334, 100335, 100336, 100337, 100338, 100339, 100340, 100341, 100342, 100343, 100344, 100345, 100346, 100347, 100348, 100349, 100350, 100351, 100352, 100353, 100354, 100355, 100356, 100357, 100358, 100359, 100360, 100361, 100362, 100363, 100364, 100365, 100366, 100367, 100368, 100369, 100370, 100371, 100372, 100373, 100374, 100375, 100376, 100377, 100378, 100379, 100380, 100381, 100382, 100383, 100384, 100385, 100386, 100387, 100388, 100389, 100390, 100391, 100392, 100393, 100394, 100395, 100396, 100397, 100398, 100399, 100400, 100401, 100402, 100403, 100404, 100405, 100406, 100407, 100408, 100409, 100410, 100411, 100412, 100413, 100414, 100415, 100416, 100417, 100418, 100419, 100420, 100421, 100422, 100423, 100424, 100425, 100426, 100427, 100428, 100429, 100430, 100431, 100432, 100433, 100434, 100435, 100436, 100437, 100438, 100439, 100440, 100441, 100442, 100443, 100444, 100445, 100446, 100447, 100448, 100449, 100450, 100451, 100452, 100453, 100454, 100455, 100456, 100457, 100458, 100459, 100460, 100461, 100462, 100463, 100464, 100465, 100466, 100467, 100468, 100469, 100470, 100471, 100472, 100473, 100474, 100475, 100476, 100477, 100478, 100479, 100480, 100481, 100482, 100483, 100484, 100485, 100486, 100487, 100488, 100489, 100490, 100491, 100492, 100493, 100494, 100495, 100496, 100497, 100498, 100499, 100500, 100501, 100502, 100503, 100504, 100505, 100506, 100507, 100508, 100509, 100510, 100511, 100512, 100513, 100514, 100515, 100516, 100517, 100518, 100519, 100520, 100521, 100522, 100523, 100524, 100525, 100526, 100527, 100528, 100529, 100530, 100531, 100532, 100533, 100534, 100535, 100536, 100537, 100538, 100539, 100540, 100541, 100542, 100543, 100544, 100545, 100546, 100547, 100548, 100549, 100550, 100551, 100552, 100553, 100554, 100555, 100556, 100557, 100558, 100559, 100560, 100561, 100562, 100563, 100564, 100565, 100566, 100567, 100568, 100569, 100570, 100571, 100572, 100573, 100574, 100575, 100576, 100577, 100578, 100579, 100580, 100581, 100582, 100583, 100584, 100585, 100586, 100587, 100588, 100589, 100590, 100591, 100592, 100593, 100594, 100595, 100596, 100597, 100598, 100599, 100600, 100601, 100602, 100603, 100604, 100605, 100606, 100607, 100608, 100609, 100610, 100611, 100612, 100613, 100614, 100615, 100616, 100617, 100618, 100619, 100620, 100621, 100622, 100623, 100624, 100625, 100626, 100627, 100628, 100629, 100630, 100631, 100632, 100633, 100634, 100635, 100636, 100637, 100638, 100639, 100640, 100641, 100642, 100643, 100644, 100645, 100646, 100647, 100648, 100649, 100650, 100651, 100652, 100653, 100654, 100655, 100656, 100657, 100658, 100659, 100660, 100661, 100662, 100663, 100664, 100665, 100666, 100667, 100668, 100669, 100670, 100671, 100672, 100673, 100674, 100675, 100676, 100677, 100678, 100679, 100680, 100681, 100682, 100683, 100684, 100685, 100686, 100687, 100688, 100689, 100690, 100691, 100692, 100693, 100694, 100695, 100696, 100697, 100698, 100699, 100700, 100701, 100702, 100703, 100704, 100705, 100706, 100707, 100708, 100709, 100710, 100711, 100712, 100713, 100714, 100715, 100716, 100717, 100718, 100719, 100720, 100721, 100722, 100723, 100724, 100725, 100726, 100727, 100728, 100729, 100730, 100731, 100732, 100733, 100734, 100735, 100736, 100737, 100738, 100739, 100740, 100741, 100742, 100743, 100744, 100745, 100746, 100747, 100748, 100749, 100750, 100751, 100752, 100753, 100754, 100755, 100756, 100757, 100758, 100759, 100760, 100761, 100762, 100763, 100764, 100765, 100766, 100767, 100768, 100769, 100770, 100771, 100772, 100773, 100774, 100775, 100776, 100777, 100778, 100779, 100780, 100781, 100782, 100783, 100784, 100785, 100786, 100787, 100788, 100789, 100790, 100791, 100792, 100793, 100794, 100795, 100796, 100797, 100798, 100799, 100800, 100801, 100802, 100803, 100804, 100805, 100806, 100807, 100808, 100809, 100810, 100811, 100812, 100813, 100814, 100815, 100816, 100817, 100818, 100819, 100820, 100821, 100822, 100823, 100824, 100825, 100826, 100827, 100828, 100829, 100830, 100831, 100832, 100833, 100834, 100835, 100836, 100837, 100838, 100839, 100840, 100841, 100842, 100843, 100844, 100845, 100846, 100847, 100848, 100849, 100850, 100851, 100852, 100853, 100854, 100855, 100856, 100857, 100858, 100859, 100860, 100861, 100862, 100863, 100864, 100865, 100866, 100867, 100868, 100869, 100870, 100871, 100872, 100873, 100874, 100875, 100876, 100877, 100878, 100879, 100880, 100881, 100882, 100883, 100884, 100885, 100886, 100887, 100888, 100889, 100890, 100891, 100892, 100893, 100894, 100895, 100896, 100897, 100898, 100899, 100900, 100901, 100902, 100903, 100904, 100905, 100906, 100907, 100908, 100909, 100910, 100911, 100912, 100913, 100914, 100915, 100916, 100917, 100918, 100919, 100920, 100921, 100922, 100923, 100924, 100925, 100926, 100927, 100928, 100929, 100930, 100931, 100932, 100933, 100934, 100935, 100936, 100937, 100938, 100939, 100940, 100941, 100942, 100943, 100944, 100945, 100946, 100947, 100948, 100949, 100950, 100951, 100952, 100953, 100954, 100955, 100956, 100957, 100958, 100959, 100960, 100961, 100962, 100963, 100964, 100965, 100966, 100967, 100968, 100969, 100970, 100971, 100972, 100973, 100974, 100975, 100976, 100977, 100978, 100979, 100980, 100981, 100982, 100983, 100984, 100985, 100986, 100987, 100988, 100989, 100990, 100991, 100992, 100993, 100994, 100995, 100996, 100997, 100998, 100999, 101000, 101001, 101002, 101003, 101004, 101005, 101006, 101007, 101008, 101009, 101010, 101011, 101012, 101013, 101014, 101015, 101016, 101017, 101018, 101019, 101020, 101021, 101022, 101023, 101024, 101025, 101026, 101027, 101028, 101029, 101030, 101031, 101032, 101033, 101034, 101035, 101036, 101037, 101038, 101039, 101040, 101041, 101042, 101043, 101044, 101045, 101046, 101047, 101048, 101049, 101050, 101051, 101052, 101053, 101054, 101055, 101056, 101057, 101058, 101059, 101060, 101061, 101062, 101063, 101064, 101065, 101066, 101067, 101068, 101069, 101070, 101071, 101072, 101073, 101074, 101075, 101076, 101077, 101078, 101079, 101080, 101081, 101082, 101083, 101084, 101085, 101086, 101087, 101088, 101089, 101090, 101091, 101092, 101093, 101094, 101095, 101096, 101097, 101098, 101099, 101100, 101101, 101102, 101103, 101104, 101105, 101106, 101107, 101108, 101109, 101110, 101111, 101112, 101113, 101114, 101115, 101116, 101117, 101118, 101119, 101120, 101121, 101122, 101123, 101124, 101125, 101126, 101127, 101128, 101129, 101130, 101131, 101132, 101133, 101134, 101135, 101136, 101137, 101138, 101139, 101140, 101141, 101142, 101143, 101144, 101145, 101146, 101147, 101148, 101149, 101150, 101151, 101152, 101153, 101154, 101155, 101156, 101157, 101158, 101159, 101160, 101161, 101162, 101163, 101164, 101165, 101166, 101167, 101168, 101169, 101170, 101171, 101172, 101173, 101174]
graphsense_statistics = general_api.get_statistics()
latest_block_height = [statistic['no_blocks'] - 1
                        for statistic in graphsense_statistics['currencies'] if statistic['name'] == 'btc'][0]

get_transactions_from_blocks(hundretusen)
for block_height in range(200000, latest_block_height, 100000):
    print("getting transactions from block", block_height)
    get_transactions_from_blocks(get_blocks(block_height, 10000))