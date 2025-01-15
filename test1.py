from dotenv import load_dotenv
import os
from binance.client import Client
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


