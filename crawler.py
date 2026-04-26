import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

visited = set()
chunks = []

def clean(text):
    return " ".join(text.split())

def split(text, size=400):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]
def crawl(url, base):
    print("Sto leggendo:", url)
    if url in visited or base not in url:
        return

    visited.add(url)

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()

        text = clean(soup.get_text())

        for chunk in split(text):
            chunks.append(chunk)

        for link in soup.find_all("a", href=True):
            crawl(urljoin(url, link["href"]), base)

    except:
        pass

crawl("https://www.autoguarizione.it", "autoguarizione.it")

import json
with open("data.json","w",encoding="utf-8") as f:
    json.dump(chunks,f)