import slack_sdk
import datetime

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

        # 포지션에 따른 색상과 이모지 설정
        if resp['side'] == 'BUY':
            color = "#36a64f"  # 초록색
            position_emoji = "🔵"
        else:
            color = "#ff4444"  # 빨간색
            position_emoji = "🔴"

        # 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*트레이딩 신호 감지* {position_emoji}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*거래쌍:*\n{resp['symbol']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*포지션:*\n{resp['side']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*주문유형:*\n{resp['type']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*수량:*\n{resp['origQty']}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"상태: {resp['status']} | 주문시각: {resp['updateTime']}"
                    }
                ]
            }
        ]

        # 기본 텍스트 메시지
        summary_text = f"{tag} {position_emoji} {resp['symbol']} {resp['side']} 포지션 {resp['origQty']} 수량"

        response = self.client.chat_postMessage(
            channel=self.channel,
            text=summary_text,
            attachments=[
                {
                    "color": color,
                    "blocks": blocks,
                    "fallback": summary_text
                }
            ]
        )
        
        return {
            'statusCode': 200,
            'body': 'send message success'
        }

    def send_error(self, error):
        if self.user_id == None:
            tag = ''
        else:
            tag = f'<@{self.user_id}>'

        # 에러 메시지 블록 구성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⚠️ 거래 실패 알림*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*에러 내용:*\n{error}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"발생 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        # 기본 텍스트 메시지
        summary_text = f"{tag} ⚠️ 거래 실패: {error}"

        response = self.client.chat_postMessage(
            channel=self.channel,
            text=summary_text,
            attachments=[
                {
                    "color": "#FF0000",  # 빨간색으로 에러 표시
                    "blocks": blocks,
                    "fallback": summary_text
                }
            ]
        )

        return {
            'statusCode': 400,
            'body': error
        }