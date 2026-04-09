import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time

client = OpenAI(api_key="TU_API_KEY")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_SCORE = 0
MAX_PRICE = 2000
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

# if not ai_decision(title_text, price_text, margin):
#     continue

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


# ---------------- MILANUNCIOS ----------------
def search_milanuncios(keyword):

    url = f"https://www.milanuncios.com/anuncios/{keyword}.htm"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    print("STATUS MILANUNCIOS:", r.status_code)

    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.find_all("article")

    print("Items trobats:", len(items))

    for item in items[:10]:

        a = item.find("a")

        if not a:
            continue

        title = a.get("title")
        link = a.get("href")

        if not title or not link:
            continue

        full_link = "https://www.milanuncios.com" + link

        if full_link in seen:
            continue

        seen.add(full_link)

        # preu aproximat
        price_text = "?"
        price_num = 400

        if price_num > MAX_PRICE:
            continue

        score, margin = investment_score(title, str(price_num), 450)

        if score < MIN_SCORE:
            continue

        print("ENVIANDO:", title)

        msg = f"""💰 CHOLLO INVERSIÓN

🎮 {title}
💸 Precio estimado: {price_text}

🔗 {full_link}
"""

        send_telegram(msg)

# ---------------- LOOP ----------------
while True:
    print("Analizando oportunidades de inversión...")

    for kw in KEYWORDS:
     search_milanuncios(kw)

    time.sleep(60)