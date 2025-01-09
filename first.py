import os
from dotenv import load_dotenv, find_dotenv
from binance.client import Client
from binance.enums import *

dotenv_file = find_dotenv()
load_dotenv()

secret_env = os.getenv("secret_key")
api_env = os.getenv("API_key")

client = Client(api_env,secret_env)
'''
order = client.create_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.0072')

orders = client.get_all_orders(symbol='BNBBTC', limit=10)
print(orders)

#지정가 구매 & 판매
order = client.order_limit_buy(
    symbol='BNBBTC',
    quantity=100,
    price='0.0072')

order = client.order_limit_sell(
    symbol='BNBBTC',
    quantity=100,
    price='0.0072')

#하나의 주문이 체결되는 즉시 나머지 주문들은 자동 취소
order = client.create_oco_order(
    symbol='BNBBTC',
    side=SIDE_SELL,
    stopLimitTimeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    stopPrice='0.00722',
    price='0.0.0072')

'''

#새로운 주문을 생성하고 검증하면서 거래소로 전송하지는 X (테스트용)  --> 핑 보내기
order = client.create_test_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.0072')

print(order)

# 주문 상태 확인
order = client.get_order(
    symbol='BNBBTC',
    orderId='orderId')

# 주문 취소
result = client.cancel_order(
    symbol='BNBBTC',
    orderId='orderId')

# 모든 미결 주문 가져오기
orders = client.get_open_orders(symbol='BNBBTC')

# 전에 했던 모든 주문 가져오기
orders = client.get_all_orders(symbol='BNBBTC')

# 자산 잔액 확인하기
balance = client.get_asset_balance(asset='BTC')

# 최근 거래 가져오기
trades = client.get_recent_trades(symbol='BNBBTC')

