import slack_sdk
import os
from dotenv import load_dotenv
import json

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")


def send_message(event, resp):

    client = slack_sdk.WebClient(token=BOT_TOKEN)

    slack_msg = f'<@{USER_ID}> test ping\n' 

    response = client.chat_postMessage(
        channel="trading",
        text=slack_msg
    )

    return {
        'statusCode' : 200,
        'body':json.dumps(response)
    }

def send_error(error):
    client = slack_sdk.WebClient(token=BOT_TOKEN)

    slack_msg = f'<@{USER_ID}> test {error}\n' 

    response = client.chat_postMessage(
        channel="trading",
        text=slack_msg
    )

    return {
        'statusCode' : 400,
        'body':json.dumps(error)
    }