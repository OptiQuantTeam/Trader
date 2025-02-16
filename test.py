import json
import os
from dotenv import load_dotenv

from binance.client import Client
from binance.enums import *

from utils import get_configure, send_message, futures_market_params, send_error

load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")



'''
*** event ***                   *** config ***
    price                           user_id
    symbol                          ratio
    side                            leverage
    positionSide                    type

'''
'''
event={'test': 'test'}
config = get_configure()

client = Client(API_KEY, SECRET_KEY)
balance = client.get_asset_balance(asset='USDT')
print(balance)
response = client.create_test_order(
    symbol=event['symbol'],
    side=event['side'],
    type=config['type'],
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=1,
    price='97809')
response = client.ping()
send_message(event, response)
'''
try:
    di = 10/0
except Exception as e:
    print(e)