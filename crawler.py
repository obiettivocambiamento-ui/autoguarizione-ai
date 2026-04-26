import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag

START_URLS = [
    "https://www.autoguarizione.it/proposte/",
    "https://www.autoguarizione.it/percorso/",
    "https://www.autoguarizione.it/analisi/",
    "https://www.autoguarizione.it/heart-bed/",
    "https://www.autoguarizione.it/biorisonanza/",
    "https://www.autoguarizione.it/nutrizione/",
    "https://www.autoguarizione.it/cristo/",
    "https://www.autoguarizione.it/risorse/",
    "https://www.autoguarizione.it/integratori/",
    "https://www.autoguarizione.it/pressione-sanguigna/",
    "https://www.autoguarizione.it/peso-2/",
    "https://www.autoguarizione.it/nutrizione-e-idratazione/",
    "https://www.autoguarizione.it/attivita-2/",
    "https://www.autoguarizione.it/respirazione/",
    "https://www.autoguarizione.it/diario-2/",
    "https://www.autoguarizione.it/scopri-coscienza/",
    "https://www.autoguarizione.it/biblioteca-domestica/",
    "https://www.autoguarizione.it/la-mia-agenda/",
    "https://www.autoguarizione.it/mappa-della-coscienza/",
    "https://www.autoguarizione.it/valore/",
    "https://www.autoguarizione.it/economia-circolare-del-dono/",
    "https://www.autoguarizione.it/donazione/"
]

BASE = "autoguarizione.it"

visited = set()
chunks = []

def clean(text):
    return " ".join(text.split())

def split(text, size=300):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]


def normalize(url):
    url, _ = urldefrag(url)  # elimina #anchor
    return url.split("?")[0].rstrip("/")


def crawl(url, depth):
    url = normalize(url)

    if url in visited:
        return

    if depth > 2:
        return

    if BASE not in url:
        return

    visited.add(url)

    print(f"[D{depth}] {url}")

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()

        text = clean(soup.get_text())

        for chunk in split(text):
            chunks.append({
                "url": url,
                "depth": depth,
                "text": chunk
            })

        # 🔥 link extraction
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            href = normalize(href)

            if BASE in href:
                crawl(href, depth + 1)

    except Exception as e:
        print("Errore:", url, e)


# 🚀 START
for url in START_URLS:
    crawl(url, 0)


import json
with open("data.json","w",encoding="utf-8") as f:
    json.dump(chunks,f, ensure_ascii=False)

print("FATTO")
print("Pagine visitate:", len(visited))
print("Chunks:", len(chunks))