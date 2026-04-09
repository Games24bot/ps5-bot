import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time

client = OpenAI(api_key="TU_API_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_SCORE = int(os.getenv("MIN_SCORE", "5"))

MAX_PRICE = 1000
KEYWORDS = ["ps5"]
seen = set()


# ---------------- TELEGRAM ----------------
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    
    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)

# ---------------- PRECIO MERCADO (SIMULADO) ----------------
def get_market_price(keyword):

    # En versión PRO real, aquí scrapeas eBay "vendidos"
    # Ahora simulamos:

    market_prices = {
        "ps5": 450,
        "playstation 5": 450
    }

    return market_prices.get(keyword.lower(), 400)


# ---------------- SCORE INVERSOR ----------------
def investment_score(title, price, market_price):

    try:
        price = float(price.replace("€", "").replace(",", "."))
    except:
        return 0, 0

    margin = market_price - price
    score = 0

    # margen
    if margin > 200:
        score += 5
    elif margin > 100:
        score += 3
    elif margin > 50:
        score += 1
    else:
        score -= 3

    # palabras clave
    if any(kw.lower() in title.lower() for kw in KEYWORDS):
     score += 2

    if "averiada" in title.lower() or "reparar" in title.lower():
        score -= 5

    return score, margin


# ---------------- IA DECISION ----------------
def ai_decision(title, price, margin):

    prompt = f"""
    Eres un experto en inversión y reventa.

    Producto: {title}
    Precio compra: {price}
    Margen estimado: {margin}€

    ¿Es buena inversión para comprar y revender?

    Responde SOLO:
    SI o NO
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return res.choices[0].message.content.strip().upper() == "SI"

    except:
        return False


# ---------------- EBAY ----------------
def search_ebay(keyword):

    url = f"https://www.ebay.es/sch/i.html?_nkw={keyword}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select(".s-item")

    for item in items[:10]:

        title = item.select_one(".s-item__title")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")

        if not title or not price or not link:
            continue

        title_text = title.text
        price_text = price.text
         
        try:
             price_num = float(price_text.replace("€", "").replace(",", ".").split()[0])
        except:
         continue

         # FILTRE DE PREU
        if price_num > MAX_PRICE:
         continue
        url_item = link["href"]

        if url_item in seen:
            continue

        seen.add(url_item)

        market_price = get_market_price(keyword)

        score, margin = investment_score(title_text, price_text, market_price)

        if score < MIN_SCORE:
            continue

        if not ai_decision(title_text, price_text, margin):
            continue

        msg = f"""💰 CHOLLO INVERSIÓN

🎮 {title_text}
💸 Compra: {price_text}
📈 Margen estimado: {margin}€

🔗 {url_item}
"""

        print("Items trobats:", len(items))
        send_telegram(msg)

# ---------------- LOOP ----------------
while True:
    print("Analizando oportunidades de inversión...")

    for kw in KEYWORDS:
        search_ebay(kw)

    time.sleep(60)
