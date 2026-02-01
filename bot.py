import os
import time
import requests
from binance.client import Client
from telegram import Bot

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (НИЧЕГО СЮДА НЕ ВСТАВЛЯТЬ) ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "600"))  # по умолчанию 10 минут
MIN_BORROW_USD = float(os.getenv("MIN_BORROW_USD", "500000"))  # фильтр

# ======================================================

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def get_margin_data():
    url = "https://api.binance.com/sapi/v1/margin/borrow-repay"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    params = {"recvWindow": 5000}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    return r.json()


def format_message(data):
    lines = ["📊 *Binance Margin Borrow Monitor*"]
    lines.append("`SYM | BORROW | REPAY | B/R`")

    count = 0
    for item in data:
        symbol = item.get("asset")
        borrow = float(item.get("borrowed", 0))
        repay = float(item.get("repaid", 0))

        if borrow < MIN_BORROW_USD:
            continue

        ratio = round(borrow / max(repay, 1), 2)

        lines.append(
            f"`{symbol:<4} | {borrow:>9,.0f} | {repay:>9,.0f} | {ratio:>5}`"
        )
        count += 1

        if count >= 20:
            break

    if count == 0:
        lines.append("_Нет активов по фильтру_")

    return "\n".join(lines)


def main():
    while True:
        try:
            data = get_margin_data()
            message = format_message(data)
            bot.send_message(
                chat_id=TELEGRAM_USER_ID,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.send_message(
                chat_id=TELEGRAM_USER_ID,
                text=f"❌ Ошибка бота: {e}"
            )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
