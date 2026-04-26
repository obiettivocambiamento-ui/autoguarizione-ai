from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, re

app = Flask(__name__)
CORS(app)

# =========================
# CARICA DATI
# =========================
data = []

if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

print("PAGINE:", len(data))


# =========================
# PULIZIA TESTO SERIA
# =========================
def clean_text(text):

    # rimuovi roba inutile
    text = re.sub(r"cookie|consenso|privacy.*", "", text, flags=re.I)

    # togli caratteri strani
    text = re.sub(r"\s+", " ", text)

    # taglia lunghezza
    return text[:800]


# =========================
# RICERCA MIGLIORATA
# =========================
def search(query):

    q_words = query.lower().split()
    results = []

    for page in data:
        text = page.get("text", "").lower()

        score = sum(1 for w in q_words if w in text)

        if score > 0:
            results.append((score, page))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:3]]


# =========================
# RISPOSTA INTELLIGENTE BASE
# =========================
def build_answer(results):

    if not results:
        return "Non ho trovato informazioni precise su questo nel sito."

    answers = []

    for r in results:
        text = clean_text(r.get("text", ""))
        answers.append(text)

    # unisci ma separa bene
    final = "\n\n---\n\n".join(answers[:2])

    return final


# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        req = request.get_json()
        user = req.get("message", "")

        results = search(user)
        answer = build_answer(results)

        reply = f"""Ecco cosa ho trovato nel sito:

{answer}

👉 Vuoi che ti riassuma meglio questo contenuto?
"""

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERRORE:", e)
        return jsonify({"reply": "Errore interno"}), 500


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