import json
import os
from dotenv import load_dotenv

from binance.client import Client
from binance.enums import *

from utils import get_configure, futures_market_params, \
                futures_limit_params, spot_limit_params, spot_market_params, \
                SlackBot



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
        config = get_configure(AWS_USER_ID)
        client = Client(config['api_key'], config['secret_key'])
        slackBot = SlackBot(config['slack_token'], config['slack_channel'], config['slack_user'])

        balance = client.futures_account_balance(asset='USDT')
        usdt = float([asset['balance'] for asset in balance if asset['asset'] == 'USDT'][0])
        slackBot.send_message(event, usdt)
        server_time = client.get_server_time()
        slackBot.send_message(event, server_time)
        server_timestamp = server_time['serverTime']
        
        slackBot.send_message(event, '테스트111111')
        if event['trade'] == 'futures':
            client.futures_change_leverage(leverage=int(config['leverage']), symbol=event['symbol'])
            
            if config['type'] == 'MARKET':
                params = futures_market_params(event=event, config=config, balance=balance)
                slackBot.send_message(event, '테스트222222')
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


