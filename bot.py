import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

KEYWORDS = [
    "ps5",
    "playstation 5",
    "ps5 slim",
    "ps5 digital"
]

MAX_PRICE = 400
CHECK_INTERVAL = 60

seen_ids = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def score_item(item):
    score = 0

    title = item["title"].lower()
    price = item["price"]
    desc = item.get("description", "").lower()

    # 💰 Precio lógico
    if 250 <= price <= 400:
        score += 2
    elif price < 200:
        score -= 5

    # 🧠 Palabras positivas
    good_words = ["factura", "ticket", "garantia", "precintada"]
    if any(word in desc for word in good_words):
        score += 2

    # 🚨 Palabras peligrosas
    bad_words = ["bizum", "transferencia", "solo envio", "urgente"]
    if any(word in desc for word in bad_words):
        score -= 3

    # ❌ basura
    if "caja" in title or "solo caja" in desc:
        score -= 5

    return score

def search_wallapop(keyword):
    url = f"https://api.wallapop.com/api/v3/search?keywords={keyword}&price_to={MAX_PRICE}"
    headers = {"User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",}

    try:
        r = requests.get(url, headers=headers)

if r.status_code != 200:
    print("Error HTTP:", r.status_code)
    return

try:
    data = r.json()
except Exception as e:
    print("Error parsing JSON:", e)
    print("Respuesta:", r.text)
    return

        for item in data.get("search_objects", []):
            item_id = item["id"]

            if item_id in seen_ids:
                continue

            seen_ids.add(item_id)

            score = score_item(item)

            if score < 2:
                continue

            title = item["title"]
            price = item["price"]
            url_item = item["web_slug"]

            msg = f"""🔥 CHOLLO DETECTADO

🎮 {title}
💰 {price}€
⚡ Score: {score}/5

https://wallapop.com/item/{url_item}
"""

            send_telegram(msg)

    except Exception as e:
        print("Error:", e)

while True:
    for kw in KEYWORDS:
        search_wallapop(kw)

    time.sleep(CHECK_INTERVAL)