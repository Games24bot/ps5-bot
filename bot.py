import os
os.system("playwright install chromium")
import time
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

KEYWORDS = ["ps5", "playstation 5"]
MAX_PRICE = 400

seen_ids = set()


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def search_wallapop(keyword):
    with sync_playwright() as p:
        browser = p.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled"
    ]
)
        page = browser.new_page()

        page.set_extra_http_headers({
    "User-Agent": "Mozilla/5.0"
})
        url = f"https://es.wallapop.com/app/search?keywords={keyword}"
        page.goto(url, timeout=60000)

        time.sleep(5)  # simula comportamiento humano

        items = page.query_selector_all("a")

        print("Items encontrados:", len(items))

        for item in items[:10]:
            try:
                title = item.inner_text()
                link = item.get_attribute("href")

                if not link or link in seen_ids:
                    continue

                seen_ids.add(link)

                if any(k.lower() in title.lower() for k in KEYWORDS):
                    msg = f"🔥 CHOLLO\n{title}\nhttps://wallapop.com{link}"
                    send_telegram(msg)

            except:
                continue

        browser.close()


while True:
    for kw in KEYWORDS:
        search_wallapop(kw)

    time.sleep(300)  # cada 5 minutos