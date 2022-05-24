from requests_html import HTMLSession
from tqdm import tqdm
from time import sleep

session = HTMLSession()
fees = []
for block in tqdm(range(200000,737731, 5000)):
    sleep(1)
    response = session.get(f'https://www.blockchain.com/btc/block/{block}')
    data = response.html.find('span')
    fee_reward = [data[i+1].text for i, d in enumerate(data) if "Fee Reward" in d.text][0]
    no_transactions = [data[i+1].text for i, d in enumerate(data) if "Number of Transactions" in d.text][0]

    fee_reward = (float(fee_reward[0:-3]))
    no_transaction = (float(no_transactions.replace(",", "."))*1000)
    fees.append(fee_reward/no_transaction)
print(fees)