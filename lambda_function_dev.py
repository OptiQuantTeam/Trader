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

        # 거래 타입 확인
        if info['trade'] != 'futures':
            raise Exception(f"Invalid Trade : {info['trade']}")
        
        # 매매 타입 확인
        if info['type'] != 'MARKET':
            raise Exception(f"Invalid Type : {info['type']}")
        
        '''
        # 현재 포지션 정보 조회
        positions = client.futures_position_information(symbol=event['symbol'])
        current_position = positions[0]['positionAmt']
        '''

        # 최근 2개의 수입 내역 확인
        income = client.futures_income_history(symbol=event['symbol'], incomeType='REALIZED_PNL', limit=2)


        '''
            최근 2개의 수입 내역 확인
            손해일 경우: 레베리지 감소
            이익일 경우: 레베리지 증가
        '''
        # 연승/연패 확인 로직
        if len(income) < 2:
            income1 = True
            income2 = True
        else:
            income1 = float(income[0]['income']) > 0
            income2 = float(income[1]['income']) > 0

        # 레버리지 변경
        leverage = int(config['leverage'])
        if income1 and income2:
            # 연승, 레버리지 변화율 수정 예정
            leverage = int(leverage) + 1
        elif not income1 and not income2:
            # 연패, 레버리지 변화율 수정 예정
            leverage = int(leverage) - 1
        else:
            # 연승/연패 아님
            leverage = int(config['leverage'])
            
        client.futures_change_leverage(leverage=leverage, symbol=info['symbol'])

        # 잔고 조회
        balance = client.futures_account_balance()
        usdt = float([asset['balance'] for asset in balance if asset['asset'] == 'USDT'][0])
        
        # 서버 시간 조회
        server_time = client.get_server_time()
        server_timestamp = server_time['serverTime']

        # 매매 파라미터 생성
        params = utils.futures_market_params(info=info, config=config, asset=usdt)
        
        # 시장가 매매 주문
        order = client.futures_create_test_order(
            symbol=params['symbol'],
            side=params['side'],
            #positionSide=params['positionSide'],
            type=params['type'],
            quantity=1,
            newOrderRespType='FULL',
            timestamp=server_timestamp)
        
        # 주문 결과 전송
        slackBot.send_message(info, order) 

        # 레버리지 변경 저장
        utils.set_leverage(AWS_USER_ID, leverage)

        response = {'statusCode': 200, 'body': 'success'}
    except Exception as e:
        slackBot.send_error(e)
        response = {'statusCode': 400, 'body': e}
    finally:
        return response


