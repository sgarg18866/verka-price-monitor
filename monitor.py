#!/usr/bin/env python3
"""
Production-ready monitor skeleton for Swiggy Instamart Verka Double Toned Milk Yellow 500 ml.
Fill SEARCH_URL if needed.
"""
import os,time,json,logging,requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SEARCH_URL="https://www.swiggy.com/api/instamart/search/v2?offset=0&ageConsent=false&layoutId=4771&voiceSearchTrackingId=&storeId=1387905&primaryStoreId=1387905&secondaryStoreId="
STATE_FILE="state.json"
THRESHOLD=30
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")

def load():
    try:return json.load(open(STATE_FILE))
    except:return {"price":None,"stock":None}
def save(s): json.dump(s,open(STATE_FILE,"w"))
def tg(msg):
    b=os.environ["TELEGRAM_BOT_TOKEN"];c=os.environ["TELEGRAM_CHAT_ID"]
    requests.post(f"https://api.telegram.org/bot{b}/sendMessage",data={"chat_id":c,"text":msg},timeout=20)
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for i in x: yield from walk(i)
def main():
    cookie=os.environ["SWIGGY_COOKIE"]
    s=requests.Session()
    r=Retry(total=3,backoff_factor=1,status_forcelist=[429,500,502,503,504],allowed_methods=["GET"])
    s.mount("https://",HTTPAdapter(max_retries=r))
    resp=s.get(SEARCH_URL,headers={"cookie":cookie,"accept":"application/json"},timeout=30)
    resp.raise_for_status()
    data=resp.json()
    prod=None
    for o in walk(data):
        if o.get("displayName")=="Verka Double Toned Milk Yellow" and o.get("quantityDescription")=="500 ml":
            prod=o;break
    if not prod: raise RuntimeError("Product not found")
    price=prod["price"]["offerPrice"]["units"]
    stock=bool(prod["inventory"]["inStock"])
    st=load()
    if stock and not st.get("stock"): tg(f"? Back in stock @ ?{price}")
    if price<=THRESHOLD and price!=st.get("price"): tg(f"?? Price dropped/changed: ?{price}")
    save({"price":price,"stock":stock})
    logging.info("price=%s stock=%s",price,stock)
if __name__=="__main__":
    main()