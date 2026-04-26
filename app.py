from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, re

app = Flask(__name__)
CORS(app)

# =========================
# LOAD DATA
# =========================
data = []

if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 👇 PRENDI SOLO IL CAMPO TEXT
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and "text" in item:
                data.append(item["text"])
            else:
                data.append(str(item))

print("PAGINE CARICATE:", len(data))


# =========================
# CLEAN TEXT SERIO
# =========================
def clean(text):
    text = str(text)

    # rimuove html
    text = re.sub(r"<[^>]+>", " ", text)

    # rimuove cookie / menu / wordpress
    blacklist = [
        "cookie", "consenso", "menu", "navigazione",
        "gestisci", "privacy", "statistiche",
        "wordpress", "login", "preferenze"
    ]

    for w in blacklist:
        text = re.sub(w, "", text, flags=re.IGNORECASE)

    # spazi
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================
# SEARCH MIGLIORATA
# =========================
def search(query):
    query = query.lower()
    results = []

    for chunk in data:
        text = chunk.lower()

        score = sum(1 for w in query.split() if w in text)

        if score > 0:
            results.append((score, chunk))

    results.sort(reverse=True)

    return [r[1] for r in results[:3]]


# =========================
# FORMATTA RISPOSTA (UMANA)
# =========================
def format_answer(text):
    text = clean(text)

    # taglia
    text = text[:800]

    # aggiunge paragrafi leggibili
    sentences = text.split(". ")

    formatted = "\n\n".join(sentences[:5])

    return formatted


# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json()
    user = req.get("message", "")

    results = search(user)

    if not results:
        return jsonify({
            "reply": "Non ho trovato informazioni chiare nel sito su questo argomento."
        })

    # prendi il risultato migliore
    best = results[0]

    answer = format_answer(best)

    reply = f"""
Ecco cosa ho trovato sul sito:

{answer}

👉 Vuoi che ti riassuma meglio o più chiaramente?
"""

    return jsonify({"reply": reply})


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "AI attiva"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)