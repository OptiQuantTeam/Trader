import json
import os
from dotenv import load_dotenv
import datetime
from binance.client import Client
from binance.enums import *
import time
import utils
from utils import SlackBot, get_symbol_info


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
    opCode                          tp
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
        response = {'statusCode': 401, 'body': str(e)}
        return response
    
    order = None
    stop_order = None

    try:
        if event.get('mode', None) == 'test':
            price_ticker = client.futures_symbol_ticker(symbol=info['symbol'])
            info['price'] = float(price_ticker['price'])

        # 거래 타입 확인
        if info.get('trade', None) != 'futures':
            raise Exception(f"Invalid Trade : {info['trade']}")
        
        # 매매 타입 확인
        if config.get('type', None) != 'MARKET':
            raise Exception(f"Invalid Type : {config['type']}. Only MARKET type is currently supported by this logic flow.")

        # 잔고 조회
        balance = client.futures_account_balance()
        usdt = float([asset['balance'] for asset in balance if asset['asset'] == 'USDT'][0])
        
        # 서버 시간 조회
        server_time = client.get_server_time()
        server_timestamp = server_time['serverTime']

        # 매매 파라미터 생성
        params = utils.futures_market_params(client=client, info=info, config=config, asset=usdt)
        
        # 최근 3개의 수입 내역 확인
        income = utils.get_income(client, params['symbol'])

        # 레버리지 조정
        leverage = utils.adjust_leverage(income, params['leverage'])

        trade_action_result = utils.process_trade_logic(
            client=client,
            symbol=params['symbol'],
            order_side=params['side'],
            order_quantity=params['quantity'],
            order_type=params['type'],
            leverage=leverage
        )

        if trade_action_result:
            order = trade_action_result
            
            # 포지션 정리인 경우
            if order.get('reduceOnly', False):
                slackBot.send_close_position(info, order)
            # 새로운 포지션을 여는 경우
            elif order.get('side') == params['side']:
                actual_entry_price = info['price']
                if order.get('fills') and len(order['fills']) > 0:
                    total_price_sum = sum(float(f['price']) * float(f['qty']) for f in order['fills'])
                    total_qty_sum = sum(float(f['qty']) for f in order['fills'])
                    if total_qty_sum > 0:
                        actual_entry_price = total_price_sum / total_qty_sum
                
                # Stop Loss 가격 계산
                stop_price_calculated = utils.calculate_stop_loss_price(
                    entry_price=actual_entry_price,
                    position_side=order['side'],
                    leverage=leverage
                )
                
                # Take Profit 가격 계산
                take_profit_price_calculated = utils.calculate_take_profit_price(
                    entry_price=actual_entry_price,
                    position_side=order['side'],
                    leverage=leverage
                )
                
                symbol_details = get_symbol_info(client, params['symbol'])
                price_precision = symbol_details['pricePrecision'] if symbol_details else 2
                stop_price_rounded = round(stop_price_calculated, price_precision)
                take_profit_price_rounded = round(take_profit_price_calculated, price_precision)

                stop_loss_order_side = Client.SIDE_SELL if order['side'] == Client.SIDE_BUY else Client.SIDE_BUY
                take_profit_order_side = Client.SIDE_SELL if order['side'] == Client.SIDE_BUY else Client.SIDE_BUY

                # Stop Loss 주문
                stop_order = client.futures_create_order(
                    symbol=params['symbol'],
                    side=stop_loss_order_side,
                    type='STOP_MARKET',
                    stopPrice=stop_price_rounded,
                    closePosition=True,
                    newOrderRespType='FULL',
                    timestamp=server_timestamp
                )

                # Take Profit 주문
                take_profit_order = client.futures_create_order(
                    symbol=params['symbol'],
                    side=take_profit_order_side,
                    type='TAKE_PROFIT_MARKET',
                    stopPrice=take_profit_price_rounded,
                    closePosition=True,
                    newOrderRespType='FULL',
                    timestamp=server_timestamp
                )

                slackBot.send_message(info, order)
                if stop_order:
                    slackBot.send_message(info, stop_order)
                if take_profit_order:
                    slackBot.send_message(info, take_profit_order)
                # 레버리지 변경 저장
                utils.set_leverage(AWS_USER_ID, leverage)
        else:
            pass

        
        response = {'statusCode': 200, 'body': 'success'}
    except Exception as e:
        slackBot.send_error(str(e))
        response = {'statusCode': 400, 'body': str(e)}
    finally:
        return response


