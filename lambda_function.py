import json
import os
from dotenv import load_dotenv

from binance.client import Client
from binance.enums import *

import utils
from utils import SlackBot



'''
Binance API <- AWS DynamoDB
Slack API   <- AWS DynamoDB
AWS API     <- AWS Lambda Env --> lambda 안에서는 필요 없음
'''
load_dotenv()

AWS_USER_ID = os.getenv('AWS_USER_ID')          #.env파일에서 AWS Lambda 환경변수로 변경할 예정

'''
*** event ***                   *** config ***
    price                           user_id
    symbol                          ratio
    side                            leverage
    positionSide                    type
    trade                           sl
                                    tp
                                    api_key
                                    secret_key
                                    slack_token
                                    slack_user
                                    slack_channel
'''

def lambda_handler(event, context):
    try:
        config = utils.get_configure(AWS_USER_ID)
        client = Client(config['api_key'], config['secret_key'])
        slackBot = SlackBot(config['slack_token'], config['slack_channel'], config['slack_user'])
        
        if event.get('mode', None) == 'test':
            price = client.futures_symbol_ticker(symbol=event['symbol'])['price']
            event['price'] = float(price)
        
        balance = client.futures_account_balance()
        usdt = float([asset['balance'] for asset in balance if asset['asset'] == 'USDT'][0])
        
        server_time = client.get_server_time()
        server_timestamp = server_time['serverTime']
        
        if event['trade'] == 'futures':
            client.futures_change_leverage(leverage=int(config['leverage']), symbol=event['symbol'])
            
            if config['type'] == 'MARKET':
                params = utils.futures_market_params(event=event, config=config, asset=usdt)
                #futures_create_order
                order = client.futures_create_test_order(
                    symbol=params['symbol'],
                    side=params['side'],
                    positionSide=params['positionSide'],
                    type=params['type'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                
                response = slackBot.send_message(event, order)  
                
            else:
                raise Exception(f"Invalid Type : {event['type']}")
            '''
            if event['side'] == 'BUY':
                sl = client.futures_create_test_order(
                    symbol=params['symbol'],
                    side='SELL',
                    positionSide=params['positionSide'],
                    type='STOP_MARKET',
                    stopprice=params['sl'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                
                tp = client.futures_create_test_order(
                    symbol=params['symbol'],
                    side='SELL',
                    positionSide=params['positionSide'],
                    type='TAKE_PROFIT_MARKET',
                    stopprice=params['tp'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                response = slackBot.send_message(event, order, sl, tp)
                    
            elif event['side'] == 'SELL':
                response = slackBot.send_message(event, order)  

            else:
                raise Exception(f"Invalid Side : {event['side']}")
            ''' 
        
        else:
            raise Exception(f"Invalid Trade : {event['trade']}")

    except Exception as e:
        print(e)
        return slackBot.send_error(e)
    
    return response


