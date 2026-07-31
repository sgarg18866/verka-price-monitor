import requests
import os
import json

# ===== CONFIG =====
PRICE_THRESHOLD = 27

URL = "https://www.swiggy.com/api/instamart/search/v2?offset=0&ageConsent=false&layoutId=4987&voiceSearchTrackingId=&storeId=1389004&primaryStoreId=1389004&secondaryStoreId="

HEADERS = {
    "content-type": "application/json",
    "origin": "https://www.swiggy.com",
    "referer": "https://www.swiggy.com/instamart/search?query=Verka+Double+Toned+Milk",
    "user-agent": "Mozilla/5.0",
    "cookie": os.getenv("SWIGGY_COOKIE")
}

BODY = {
    "facets": [],
    "sortAttribute": "",
    "query": "Verka Double Toned Milk",
    "search_results_offset": "0",
    "page_type": "INSTAMART_AUTO_SUGGEST_PAGE",
    "is_pre_search_tag": False
}

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})


def get_last_price():
    try:
        with open("last_price.txt", "r") as f:
            return int(f.read().strip())
    except:
        return None


def save_price(price):
    with open("last_price.txt", "w") as f:
        f.write(str(price))


r = requests.post(URL, headers=HEADERS, json=BODY, timeout=20)

print("Status Code:", r.status_code)
print("Content-Type:", r.headers.get("content-type"))
print("Response:")
print(r.text[:1000])

return

def main():
    price = fetch_price()

    if price is None:
        print("Product not found")
        return

    print("Current Price:", price)

    last_price = get_last_price()

    if price < PRICE_THRESHOLD:
        if last_price != price:
            msg = f"?? Verka Milk Price Drop!\n?{price} on Swiggy Instamart"
            send_telegram(msg)
            save_price(price)
    else:
        # reset when price goes back up
        save_price(999)


if __name__ == "__main__":
    main()
