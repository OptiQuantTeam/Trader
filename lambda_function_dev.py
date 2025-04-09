import json
import os
from dotenv import load_dotenv
import datetime
from binance.client import Client
from binance.enums import *
import time
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
        info = event['info']
    except Exception as e:
        response = {'statusCode': 401, 'body': e}
        return response
    
    try:
        if event.get('mode', None) == 'test':
            price = client.futures_symbol_ticker(symbol=info['symbol'])['price']
            info['price'] = float(price)

        
        if info['trade'] == 'futures':
            # 현재 포지션 정보 조회
            positions = client.futures_position_information(symbol=event['symbol'])
            current_position = positions[0]['positionAmt']

            # SHORT 포지션 정리
            if event['side'] == 'BUY' and current_position < 0:
                close_order = client.futures_create_test_order(
                                symbol=event['symbol'],
                                side='BUY',
                                type=config['type'],
                                quantity=abs(current_position),
                                newOrderRespType='FULL',
                                timestamp=server_timestamp)
                while True:
                    # 주문 상태 확인
                    closed_order = client.futures_get_order(
                        symbol=event['symbol'],
                        orderId=close_order['orderId'])
                    if closed_order['status'] == 'FILLED' :
                        slackBot.send_close_position(event, closed_order)
                        break
                    elif closed_order['status'] == 'REJECTED' or closed_order['status'] == 'CANCELED' or closed_order['status'] == 'PENDING_CANCEL':
                        raise Exception(f"{closed_order['status']} : {closed_order['msg']}")
                    time.sleep(0.5)
                

            # LONG 포지션 정리
            elif event['side'] == 'SELL' and current_position > 0:
                close_order = client.futures_create_test_order(
                                symbol=event['symbol'],
                                side='SELL',
                                type=config['type'],
                                quantity=abs(current_position),
                                newOrderRespType='FULL',
                                timestamp=server_timestamp)
                
                while True:
                    # 주문 상태 확인
                    closed_order = client.futures_get_order(
                        symbol=event['symbol'],
                        orderId=close_order['orderId'])
                    if closed_order['status'] == 'FILLED' :
                        slackBot.send_close_position(event, closed_order)
                        break
                    elif closed_order['status'] == 'REJECTED' or closed_order['status'] == 'CANCELED' or closed_order['status'] == 'PENDING_CANCEL':
                        raise Exception(f"{closed_order['status']} : {closed_order['msg']}")
                    time.sleep(0.5)

            # 잔고 조회
            balance = client.futures_account_balance()
            usdt = float([asset['balance'] for asset in balance if asset['asset'] == 'USDT'][0])
            
            server_time = client.get_server_time()
            server_timestamp = server_time['serverTime']

            # 레버리지 변경
            client.futures_change_leverage(leverage=int(config['leverage']), symbol=info['symbol'])

            # 시장가 매매 주문
            if config['type'] == 'MARKET':
                params = utils.futures_market_params(info=info, config=config, asset=usdt)
                
                order = client.futures_create_test_order(
                    symbol=params['symbol'],
                    side=params['side'],
                    #positionSide=params['positionSide'],
                    type=params['type'],
                    quantity=1,
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                
                response = slackBot.send_message(info, order) 

            else:
                raise Exception(f"Invalid Type : {info['type']}")

        else:
            raise Exception(f"Invalid Trade : {info['trade']}")

        response = {'statusCode': 200, 'body': 'success'}
    except Exception as e:
        slackBot.send_error(e)
        response = {'statusCode': 400, 'body': e}
    finally:
        return response


