from dotenv import load_dotenv
import os
from binance.client import Client
from binance.enums import *    #test 가져오는거
import slack_sdk   # SLACK 가져오는거
# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
api_key = os.getenv('API_KEY')
secret_key = os.getenv('Secret_Key')
#print(f"API_KEY: {api_key}")
#print(f"Secret_key: {secret_key}")

#amount = 0.000234234            #주문넣을때 총량
#precision = 5
#amt_str = "{:0.0{}f}".format(amount, precision)

client = Client(api_key, secret_key)

#시장가 거래
#order = client.order_market_buy(
#    symbol='BNBBTC',
#    quantity=100)
#order = client.order_market_sell(
#    symbol='BNBBTC',
#    quantity=100)


#TEST 거래
#order = client.create_test_order(
#    symbol='BTCUSDT',    #코인이름
#    side=SIDE_BUY,       #매수,매도
#    type=ORDER_TYPE_LIMIT,  #시정가 지정가 지정하는거 
#    timeInForce=TIME_IN_FORCE_GTC,  #제한시간
#    quantity=0.01,    #살 코인 갯수
#    price='96784.3')  #갯수

"""
slack_key = os.getenv('Slack_Token')   #slack으로 매수 매도 확인
slack = slack_sdk.WebClient(token=slack_key)

user_id = "U088PN3C5FC"
slack_msg = f'<@{user_id}> 주문내역' 

response = slack.chat_postMessage(
    channel="거래",
    text=slack_msg
)
#print(response)
"""

"""
#재산 잔액
balance = client.get_asset_balance(asset='BTC')  
print(balance)
"""

"""
#계좌 상태
status = client.get_account_status()   
print(status)
"""

"""
#계정 세부정보
details = client.get_asset_details()   
print(details)
"""
