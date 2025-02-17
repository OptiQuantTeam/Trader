import json
import os
from dotenv import load_dotenv

from binance.client import Client
from binance.enums import *
from utils import get_configure, send_message, \
                futures_market_params, send_error, \
                futures_limit_params, spot_limit_params, spot_market_params


load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

'''
*** event ***                   *** config ***
    price                           user_id
    symbol                          ratio
    side                            leverage
    positionSide                    type
    trade                           sl
                                    tp
'''

def lambda_handler(event, context):
    try:
        client = Client(API_KEY, SECRET_KEY)
        balance = client.get_asset_balance(asset='USDT')
        config = get_configure()
        server_time = client.get_server_time()
        server_timestamp = server_time['serverTime']
        

        if event['trade'] == 'futures':
            client.futures_change_leverage(leverage=int(config['leverage']), symbol=event['symbol'])
            
            if config['type'] == 'MARKET':
                params = futures_market_params(event=event, config=config, balance=balance)
                print(params)
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
                
            elif config['type'] == 'LIMIT':
                params = futures_limit_params(event, config, balance)

                order = client.create_test_order(
                    symbol=params['symbol'],
                    side=params['side'],
                    positionSide=params['positionSide'],
                    type=params['type'],
                    quantity=params['quantity'],
                    timeInForce='IOC',
                    price=params['price'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
            else:
                raise Exception(f"Invalid Type : {event['type']}")
            
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
                response = send_message(event, order, sl, tp)
                    
            elif event['side'] == 'SELL':
                response = send_message(event, order)  

            else:
                raise Exception(f"Invalid Side : {event['side']}")

        elif event['trade'] == 'spot':
            if config['type'] == 'MARKET':
                params = spot_market_params(event=event, config=config, balance=balance)
                
                #futures_create_order
                order = client.create_test_order(
                    symbol=params['symbol'],
                    side=params['side'],
                    type=params['type'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                
            elif config['type'] == 'LIMIT':
                params = spot_limit_params(event, config, balance)

                order = client.create_test_order(
                    symbol=params['symbol'],
                    side=params['side'],
                    type=params['type'],
                    quantity=params['quantity'],
                    timeInForce='IOC',
                    price=params['price'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
            
            if event['side'] == 'BUY':
                sl = client.create_test_order(
                    symbol=params['symbol'],
                    side='SELL',
                    type='STOP_LOSS',
                    stopprice=params['sl'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                
                tp = client.create_test_order(
                    symbol=params['symbol'],
                    side='SELL',
                    type='TAKE_PROFIT',
                    stopprice=params['tp'],
                    quantity=1,
                    #quantity=params['quantity'],
                    newOrderRespType='FULL',
                    timestamp=server_timestamp)
                response = send_message(event, order, sl, tp)

            elif event['side'] == 'SELL':
                response = send_message(event, order)

            else:
                raise Exception(f"Invalid Side : {event['side']}")
        else:
            raise Exception(f"Invalid Trade : {event['trade']}")

    except Exception as e:
        print(e)
        return send_error(e)
    
    return response



dict={
    'trade':'futures',
    'price':96070,
    'symbol':'BTCUSDT',
    'side':'BUY',
    'positionSide':'LONG'
}
dict2={
    'trade':'spot',
    'price':96070,
    'symbol':'BTCUSDT',
    'side':'SELL',
}
print(lambda_handler(event=dict, context=''))