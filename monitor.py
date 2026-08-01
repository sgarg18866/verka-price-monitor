import os
import time
import requests

# ================= CONFIG =================

PRICE_THRESHOLD = 30

STORE_IDS = [
    "1387905",  # App / Category store
    "1389004",  # Search store
]

CATEGORY_URL = "https://www.swiggy.com/api/instamart/category-listing/v2"

PRODUCT_NAME = "Verka Double Toned Milk"

HEADERS = {
    "content-type": "application/json",
    "origin": "https://www.swiggy.com",
    "referer": "https://www.swiggy.com/instamart",
    "user-agent": "Mozilla/5.0",
    "cookie": os.getenv("SWIGGY_COOKIE")
}

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LAST_PRICE_FILE = "last_price.txt"

# ===========================================


def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=20
        )
    except Exception as e:
        print("Telegram Error:", e)


def get_last_price():
    try:
        with open(LAST_PRICE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return None


def save_price(price):
    with open(LAST_PRICE_FILE, "w") as f:
        f.write(str(price))


def find_product(obj):
    """
    Recursively search JSON for Verka Double Toned Milk
    """

    if isinstance(obj, dict):

        name = (
            obj.get("displayName")
            or obj.get("name")
            or obj.get("productName")
            or ""
        )

        if PRODUCT_NAME.lower() in name.lower():

            inventory = obj.get("inventory", {})

            price = (
                obj.get("offerPrice")
                or obj.get("price")
                or obj.get("finalPrice")
                or obj.get("sellingPrice")
            )

            if isinstance(price, dict):
                price = (
                    price.get("offerPrice")
                    or price.get("value")
                    or price.get("mrp")
                )

            return {
                "name": name,
                "price": price,
                "inventory": inventory
            }

        for value in obj.values():
            result = find_product(value)
            if result:
                return result

    elif isinstance(obj, list):

        for item in obj:
            result = find_product(item)
            if result:
                return result

    return None


def fetch_from_store(store):

    params = {
        "categoryName": "Dairy, Bread and Eggs",
        "taxonomyType": "Speciality taxonomy 1",
        "offset": 0,
        "storeId": store,
        "primaryStoreId": store,
        "secondaryStoreId": ""
    }

    for attempt in range(3):

        try:

            print(f"\nChecking Store {store} (Attempt {attempt + 1})")

            r = requests.get(
                CATEGORY_URL,
                headers=HEADERS,
                params=params,
                timeout=20
            )
			
			print("=" * 80)
            print("Status:", r.status_code)
            print("Content-Type:", r.headers.get("content-type"))
            print("URL:", r.url)
            print("Body:")
            print(r.text[:1000])
            print("=" * 80)

            print("Status:", r.status_code)

            if r.status_code != 200:
                time.sleep(2)
                continue

            #data = r.json()

            product = find_product(data)

            if not product:
                print("Milk not found in response.")
                return None

            inventory = product.get("inventory", {})

            in_stock = inventory.get("inStock", False)

            print("--------------------------------------")
            print("Product :", product["name"])
            print("Price   :", product["price"])
            print("Stock   :", in_stock)
            print("--------------------------------------")

            if in_stock:

                return {
                    "price": int(product["price"]),
                    "store": store
                }

            return None

        except Exception as e:
            print(e)
            time.sleep(2)

    return None


def fetch_price():

    for store in STORE_IDS:

        result = fetch_from_store(store)

        if result:
            return result

    return None


def main():

    result = fetch_price()

    if not result:
        print("\nMilk unavailable in all configured stores.")
        return

    price = result["price"]
    store = result["store"]

    print(f"\nFound in Store {store}")
    print(f"Current Price : ?{price}")

    last_price = get_last_price()

    if price <= PRICE_THRESHOLD:

        if last_price != price:

            msg = (
                "?? Verka Double Toned Milk\n\n"
                f"?? Price : ?{price}\n"
                f"?? Store : {store}\n\n"
                "? Available on Swiggy Instamart"
            )

            send_telegram(msg)

            save_price(price)

            print("Telegram notification sent.")

        else:
            print("Price unchanged. No notification.")

    else:

        print("Price above threshold.")

        save_price(999)


if __name__ == "__main__":
    main()