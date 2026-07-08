import time
import requests
import os

# ناخد القيم من Railway بدل ما نحطها في الكود
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

balance = 1000
risk = 0.02  # 2%

def strategy(price):
    # استراتيجية مبدئية
    if price % 2 == 0:
        return "buy"
    else:
        return "sell"

def run_bot():
    global balance

    send("🚀 البوت اشتغل!")

    while True:
        try:
            price = 100  # هنربطه API حقيقي بعدين
            signal = strategy(price)

            trade_size = balance * risk

            if signal == "buy":
                profit = trade_size * 2
                balance += profit
                send(f"📈 BUY\nProfit: {profit}\nBalance: {balance}")

            else:
                loss = trade_size
                balance -= loss
                send(f"📉 SELL\nLoss: {loss}\nBalance: {balance}")

            time.sleep(10)

        except Exception as e:
            send(f"⚠️ Error: {e}")
            time.sleep(10)

run_bot()
