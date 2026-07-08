import time
import os
import requests
import pandas as pd

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOL = "BTCUSDT"
INTERVAL = "1m"

balance = 1000
risk = 0.02

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_price():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df = df.iloc[:, :6]
    df.columns = ["time","open","high","low","close","volume"]
    df["close"] = df["close"].astype(float)
    return df

def rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(df):
    exp1 = df["close"].ewm(span=12).mean()
    exp2 = df["close"].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal

def strategy(df):
    df["RSI"] = rsi(df)
    macd_line, signal_line = macd(df)

    if df["RSI"].iloc[-1] < 30 and macd_line.iloc[-1] > signal_line.iloc[-1]:
        return "buy"
    elif df["RSI"].iloc[-1] > 70 and macd_line.iloc[-1] < signal_line.iloc[-1]:
        return "sell"
    return "hold"

def run_bot():
    global balance

    send("🚀 البوت الاحترافي اشتغل!")

    while True:
        try:
            df = get_price()
            signal = strategy(df)

            price = df["close"].iloc[-1]
            trade_size = balance * risk

            if signal == "buy":
                tp = price * 1.02
                sl = price * 0.98

                balance += trade_size * 2
                send(f"📈 BUY\nPrice: {price}\nTP: {tp}\nSL: {sl}\nBalance: {balance}")

            elif signal == "sell":
                tp = price * 0.98
                sl = price * 1.02

                balance -= trade_size
                send(f"📉 SELL\nPrice: {price}\nTP: {tp}\nSL: {sl}\nBalance: {balance}")

            else:
                send(f"⏸ HOLD\nPrice: {price}")

            time.sleep(30)

        except Exception as e:
            send(f"⚠️ Error: {e}")
            time.sleep(10)

run_bot()
