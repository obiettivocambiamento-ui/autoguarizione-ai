from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HEADERS = {}

def ask_ai(prompt):

    try:
        r = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=25
        )

        data = r.json()

        # DEBUG sicuro
        print("AI RESPONSE:", data)

        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]

        if isinstance(data, dict) and "error" in data:
            return "AI temporaneamente occupata, riprova"

        return str(data)

    except Exception as e:
        print("AI ERROR:", e)
        return "Errore AI temporaneo"


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"reply": "Messaggio vuoto"}), 400

        user_msg = data["message"]

        prompt = f"""
Sei un assistente del sito autoguarizione.it.
Rispondi in italiano semplice e chiaro.

Domanda: {user_msg}

Risposta:
"""

        reply = ask_ai(prompt)

        return jsonify({"reply": reply})

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({"reply": "Errore server interno"}), 500


@app.route("/")
def home():
    return "AI attiva"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)