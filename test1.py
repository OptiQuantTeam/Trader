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

client = Client(api_key, secret_key)

#print(f"API_KEY: {api_key}")
#print(f"Secret_key: {secret_key}")

#amount = 0.000234234            #주문넣을때 총량
#precision = 5
#amt_str = "{:0.0{}f}".format(amount, precision)

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

#재산 잔액
balance = client.get_asset_balance(asset='BTC')  
print(balance)


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



slack_key = os.getenv('Slack_Token')   #slack으로 매수 매도 확인
slack = slack_sdk.WebClient(token=slack_key)

user_id = "U088PN3C5FC"

try:
    #시장가 거래 신청 하기(BTCUSDT,매수)
    order = client.order_market_buy(
        symbol='BTCUSDT',
        quantity=0.01 #주문량
    )

    executed_qty = order['executedQty']  # 거래된 수량
    order_id = order['orderId']          # 주문 ID
    status = order['status']             # 주문 상태


    slack_msg = f"<@{user_id}> Binance Coin 주문내역:\n\n" \
                f"코인: BTCUSDT\n" \
                f"거래 유형: 매수 (시장가)\n" \
                f"거래된 수량: {executed_qty} BTC\n" \
                f"주문 상태: {status}\n" \
                f"주문 ID: {order_id}\n" \
                f"현재 계좌 남은 잔액: {balance['free']} BTC"

    response = slack.chat_postMessage(
        channel="거래",
        text=slack_msg
    )
#print(response)

except Exception as e:
    # 예외 발생 시 오류 메시지 전송
    try:
        # balance 의 남은 잔액 숫자로 형태변환
        free_balance = float(balance['free'])
    except ValueError:
        # 만약 변환이 안 되면 오류 메시지를 전송
        free_balance = 0.0  # 기본값 설정

    if free_balance <= 0.0:
        error_msg = f"<@{user_id}> 현재 계좌의 잔액이 부족합니다:\n{e}"
        slack.chat_postMessage(
            channel="거래",
            text=error_msg
        )
    else:
        error_msg = f"<@{user_id}> 시장가 거래 신청 중 오류가 발생했습니다:\n{e}"
        slack.chat_postMessage(
            channel="거래",
            text=error_msg
        )
        print(f"오류 발생: {e}")

