import time
import requests
from binance.client import Client
from telegram import Bot

# === НАСТРОЙКИ ===
BINANCE_API_KEY = ""
BINANCE_API_SECRET = ""

TELEGRAM_BOT_TOKEN = ""
TELEGRAM_USER_ID = ""  # твой user_id

CHECK_INTERVAL = 300  # секунд (5 минут)

# ==================

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def get_margin_data():
    url = "https://api.binance.com/sapi/v1/margin/borrow-repay"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    params = {"recvWindow": 5000}
    r = requests.get(url, headers=headers, params=params)
    return r.json()


def format_message(data):
    lines = ["📊 *Margin Borrow Monitor*"]
    for item in data[:15]:
        symbol = item.get("asset")
        borrow = float(item.get("borrowed", 0))
        repay = float(item.get("repaid", 0))
        if borrow > 0:
            ratio = round(borrow / max(repay, 1), 2)
            lines.append(
                f"{symbol} | BOR {borrow:,.0f} | REP {repay:,.0f} | B/R {ratio}"
            )
    return "\n".join(lines)


def main():
    while True:
        try:
            data = get_margin_data()
            msg = format_message(data)
            bot.send_message(chat_id=TELEGRAM_USER_ID, text=msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(chat_id=TELEGRAM_USER_ID, text=f"❌ Error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
