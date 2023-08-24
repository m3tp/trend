import yfinance as yf
from pytz import timezone
import pandas as pd
import requests
import time
from flask import Flask

app = Flask(__name__)

jst = timezone('Asia/Tokyo')
line_notify_token = 'imaF5GmU3W3zsvXI19pnStCVE4XOCL2ORRhw9Z1sn3c'
line_notify_api = 'https://notify-api.line.me/api/notify'
headers = {'Authorization': f'Bearer {line_notify_token}'}
previous_trend = None

def check_trend():
    data = yf.download('AUDJPY=X', period='1d', interval='1m', ignore_tz=False, auto_adjust=True, actions=False, progress=False)
    data.index = data.index.tz_convert(jst)
    data = data[['Open', 'High', 'Low', 'Close']]
    data.index = data.index.tz_localize(None)

    sma_21 = data['Close'].rolling(window=21).mean().iloc[-1]
    sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
    sma_200 = data['Close'].rolling(window=200).mean().iloc[-1]

    if sma_21 > sma_50 > sma_200:
        current_trend = "上昇トレンド"
    elif sma_200 > sma_50 > sma_21:
        current_trend = "下降トレンド"
    else:
        current_trend = "トレンドの判定が難しい"

    return current_trend

def notify_line(message):
    data = {'message': message}
    requests.post(line_notify_api, headers=headers, data=data)

@app.route('/')
def home():
    global previous_trend
    current_trend = check_trend()
    
    if current_trend != previous_trend:
        message = f"新しいトレンド: {current_trend}"
        notify_line(message)
        previous_trend = current_trend
    
    return "Hello, Flask is running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

