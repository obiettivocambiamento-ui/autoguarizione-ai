from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# =========================
# CARICA KNOWLEDGE STRUTTURATO
# =========================
with open("knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# =========================
# INTENT MATCHING (CUORE DEL SISTEMA)
# =========================
def find_page(query):

    q = query.lower()

    best = None

    for item in data:
        for intent in item["intent"]:
            if intent in q:
                return item

    # fallback intelligente
    for item in data:
        if item["id"] == "home":
            best = item

    return best


# =========================
# RISPOSTA STABILE
# =========================
def build_answer(item):

    return f"""📌 {item['title']}

{item['content']}

👉 Approfondisci qui:
{item['url']}
"""


# =========================
# CHAT API
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    user = request.json.get("message", "")

    page = find_page(user)

    if not page:
        return jsonify({
            "reply": "Non ho trovato una sezione precisa, prova a riformulare la domanda 😊"
        })

    return jsonify({
        "reply": build_answer(page),
        "source": page["id"]
    })


@app.route("/")
def home():
    return "AI MOTORE SITO ATTIVO"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)