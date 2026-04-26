from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# =========================
# CONFIG LLM (FREE HUGGINGFACE)
# =========================
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# Se vuoi puoi aggiungere token HuggingFace qui (opzionale)
HF_TOKEN = os.getenv("HF_TOKEN", "")

headers = {}
if HF_TOKEN:
    headers["Authorization"] = f"Bearer {HF_TOKEN}"


# =========================
# CARICA CONOSCENZA SITO (OPZIONALE)
# =========================
try:
    with open("knowledge.json", "r", encoding="utf-8") as f:
        knowledge = json.load(f)
    SITE_TEXT = "\n".join([k["text"] for k in knowledge])
except:
    SITE_TEXT = "Il sito tratta percorsi di consapevolezza e crescita personale."


# =========================
# FUNZIONE AI
# =========================
def generate_answer(user_message):

    prompt = f"""
Sei un assistente virtuale del sito autoguarizione.it.

Devi rispondere in modo:
- naturale
- umano
- semplice
- conversazionale
- NON copiare testi lunghi

CONTESTO DEL SITO:
{SITE_TEXT}

DOMANDA UTENTE:
{user_message}

RISPOSTA:
"""

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 250,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            },
            timeout=40
        )

        data = response.json()

        # parsing robusto HF
        if isinstance(data, list) and len(data) > 0:
            if "generated_text" in data[0]:
                return data[0]["generated_text"]

            return data[0].get("generated_text", str(data[0]))

        return str(data)

    except Exception as e:
        print("ERROR:", e)
        return "Sto avendo un problema a generare la risposta in questo momento."


# =========================
# CHAT ENDPOINT
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "")

    reply = generate_answer(user_message)

    return jsonify({
        "reply": reply
    })


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return "AI voce pro attiva"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)