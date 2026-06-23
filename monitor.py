import requests
import os

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Current prices (replace later with scraper)
milk_price = 26
curd_price = 77

milk_qty = 5

cart_total = milk_price * milk_qty + curd_price

TARGET_PRICE = 200

message = (
    f"Verka Price Check\n\n"
    f"Milk (500ml): ₹{milk_price} x {milk_qty}\n"
    f"Curd (1kg): ₹{curd_price}\n\n"
    f"Total Basket: ₹{cart_total}"
)

if cart_total <= TARGET_PRICE:
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": f"🔥 PRICE ALERT\n\n{message}"
        }
    )
else:
    print(message)
