import json
import os
from dotenv import load_dotenv
import slack_sdk
from binance.client import Client
from binance.enums import *

load_dotenv()
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

def lambda_handler(event, context):
    bi_client = Client(API_KEY, SECRET_KEY)

    side = bi_client.create_test_order(
        symbol='BTCUSDT',
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=1,
        price='97809')
    


    client = slack_sdk.WebClient(token=BOT_TOKEN)

    slack_msg = f'<@{USER_ID}> {event['side']}\n{side}' 

    response = client.chat_postMessage(
        channel="trading",
        text=slack_msg
    )
    return {
        'statusCode':200,
        'body':'success'
    }