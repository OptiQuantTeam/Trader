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

def lambda_handler(event, context):
    try:
        client = Client(API_KEY, SECRET_KEY)
        balance = client.get_asset_balance(asset='USDT')
        config = get_configure()

        if event['side'] == 'futures':

            params = futures_market_params(event, config, balance)
        
            response = client.create_test_order(
                symbol=params['symbol'],
                side=params['side'],
                type=params['type'],
                quantity=params['quantity'])
            
        elif event['side'] == 'spot':
            # 현물 거래
            pass



        slack_resp = send_message(event, response)
        if slack_resp['statusCode'] == 200:
            # 200일 때의 메시지
            pass
        elif slack_resp['statusCode'] == 400:
            # 400일 때의 메시지
            pass
        # 에러처리를 해야 함!!!!!
    except Exception as e:
        return send_error(e)
    
    
        
    return {
        'statusCode':200,
        'body':json.dumps(response)
        }