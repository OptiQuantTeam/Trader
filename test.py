import os
from dotenv import load_dotenv
import slack_sdk
from binance.client import Client
from binance.enums import *
import argparse

load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")



bi_client = Client(API_KEY, SECRET_KEY)

#bi_client.ping()
'''
asset = bi_client.create_test_order(
    symbol='BTCUSDT',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=1,
    price='97809')
print(asset)
'''
status = bi_client.get_asset_details()
print(status)
#parser = argparse.ArgumentParser()

#parser.add_argument('--target', required=True)
#args = parser.parse_args()

#print(args.target)



'''
client = slack_sdk.WebClient(token=BOT_TOKEN)

user_id = "U086P8NDFPA"
slack_msg = f'<@{user_id}> {asset}' 

response = client.chat_postMessage(
    channel="trading",
    text=slack_msg
)
#print(response)
'''