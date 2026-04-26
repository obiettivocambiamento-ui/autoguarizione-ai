from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests

app = Flask(__name__)
CORS(app)

# =========================
# CARICA KNOWLEDGE
# =========================
with open("knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

print("KNOWLEDGE CARICATO:", len(knowledge))


# =========================
# TROVA CONTENUTO MIGLIORE
# =========================
def get_context(user_question):
    q = user_question.lower()

    best = None
    best_score = 0

    for item in knowledge:
        score = sum(1 for w in item["topic"].split() if w in q)

        if score > best_score:
            best = item
            best_score = score

    if best:
        return best["content"]

    return "Non ho informazioni specifiche su questo argomento nel sito."


# =========================
# 🧠 AI (HUGGING FACE FREE)
# =========================
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

def ask_ai(question, context):

    prompt = f"""
Sei un assistente del sito autoguarizione.it.

Usa queste informazioni:

{context}

Domanda: {question}

Rispondi in modo chiaro, semplice e utile in italiano.
"""

    try:
        response = requests.post(
            API_URL,
            json={"inputs": prompt},
            timeout=20
        )

        data = response.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "")

        return "Errore AI"

    except Exception as e:
        print("ERRORE AI:", e)
        return context  # fallback intelligente


# =========================
# CHAT ENDPOINT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user = data.get("message", "")

        context = get_context(user)
        answer = ask_ai(user, context)

        return jsonify({"reply": answer})

    except Exception as e:
        print("ERRORE:", e)
        return jsonify({"reply": "Errore server"}), 500


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