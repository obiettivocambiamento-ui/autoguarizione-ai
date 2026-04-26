from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import re

app = Flask(__name__)
CORS(app)

# =========================
# 📦 LOAD DATA
# =========================
data = []

if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, list):
        data = [str(x) for x in raw]
    elif isinstance(raw, dict):
        data = [str(v) for v in raw.values()]
    else:
        data = [str(raw)]


# =========================
# 🧹 CLEAN TEXT
# =========================
def clean(text):
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# 🔎 SEARCH
# =========================
def search(query):
    query = (query or "").lower()
    results = []

    for chunk in data:
        try:
            text = str(chunk).lower()
            score = sum(1 for w in query.split() if w in text)

            if score > 0:
                results.append((score, chunk))
        except:
            continue

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:5]]


# =========================
# 🧠 SIMPLE SUMMARIZER (IMPORTANT)
# =========================
def summarize(texts):
    """
    Trasforma contenuti grezzi in risposta umana
    """
    clean_texts = [clean(t) for t in texts]

    # unisci ma limita
    joined = " ".join(clean_texts)[:1500]

    # mini "intelligenza": taglia frasi inutili
    stop_words = [
        "cookie", "consenso", "menu", "navigazione",
        "gestisci", "privacy", "wordpress", "login"
    ]

    for w in stop_words:
        joined = joined.replace(w, "")

    return joined.strip()


# =========================
# 💬 CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json(silent=True)

    if not req:
        return jsonify({"reply": "Errore richiesta"}), 400

    user = req.get("message", "")

    results = search(user)

    if not results:
        return jsonify({"reply": "Non ho trovato informazioni nel sito."})

    summary = summarize(results)

    reply = f"""
Ecco una spiegazione semplice basata sul sito:

{summary}

👉 Se vuoi, posso spiegartelo ancora più semplice.
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