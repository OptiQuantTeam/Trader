import slack_sdk
import json

class SlackBot():
    def __init__(self, BOT_TOKEN, CHANNEL, USER_ID=None):
        self.client = slack_sdk.WebClient(token=BOT_TOKEN)
        self.channel = CHANNEL
        self.user_id = USER_ID

    def send_message(self, event, resp, sl=None, tp=None):

        if self.user_id == None:
            tag = ''
        else:
            tag = f'<@{self.user_id}>'

        slack_msg = f'{tag} 거래됨\n {resp}\n' 

        response = self.client.chat_postMessage(
            channel=self.channel,
            text=slack_msg
        )
        print(response.data)
        return {
            'statusCode' : 200,
            'body': 'send message success'
        }

    def send_error(self, error):

        if self.user_id == None:
            tag = ''
        else:
            tag = f'<@{self.user_id}>'

        slack_msg = f'{tag} {error}\n' 

        response = self.client.chat_postMessage(
            channel=self.channel,
            text=slack_msg
        )

        return {
            'statusCode' : 400,
            'body':error
        }