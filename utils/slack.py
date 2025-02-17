import slack_sdk
import os
from dotenv import load_dotenv
import json

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")


def send_message(event, resp, sl=None, tp=None):

    client = slack_sdk.WebClient(token=BOT_TOKEN)

    slack_msg = f'<@{USER_ID}> {resp}\n' 

    response = client.chat_postMessage(
        channel="trading",
        text=slack_msg
    )

    return {
        'statusCode' : 200,
        'body':resp
    }

def send_error(error):
    client = slack_sdk.WebClient(token=BOT_TOKEN)

    slack_msg = f'<@{USER_ID}> error : {error}\n' 

    response = client.chat_postMessage(
        channel="trading",
        text=slack_msg
    )

    return {
        'statusCode' : 400,
        'body':error
    }