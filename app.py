import os
import traceback
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("🚀 SERVER STARTING...")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("🔑 GEMINI KEY PRESENTE:", bool(GEMINI_API_KEY))

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "OK - SERVER ATTIVO"

# =========================
# TROVA MODELLI DISPONIBILI
# =========================
def get_available_models():

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        res = requests.get(url, timeout=10)
        data = res.json()

        models = []

        for m in data.get("models", []):
            name = m.get("name", "")
            if "generateContent" in m.get("supportedGenerationMethods", []):
                models.append(name)

        print("📦 MODELLI DISPONIBILI:", models)

        return models

    except Exception:
        traceback.print_exc()
        return []


# =========================
# GEMINI CALL CORRETTA
# =========================
def call_gemini(message):

    if not GEMINI_API_KEY:
        return "Errore AI (API key mancante)"

    models = get_available_models()

    if not models:
        return "Nessun modello Gemini disponibile per questa API key"

    # usa il primo modello valido
    model = models[0]

    print("🎯 USO MODELLO:", model)

    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"{model}:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": message}]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=20)
        data = response.json()

        print("📦 GEMINI RESPONSE:", data)

        if "error" in data:
            return f"Errore Gemini API: {data['error'].get('message')}"

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception:
        traceback.print_exc()
        return "Errore interno AI"


# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(force=True)
        text = data.get("message", "")

        if not text:
            return jsonify({"reply": "Scrivi un messaggio"}), 200

        print("💬 USER:", text)

        reply = call_gemini(text)

        return jsonify({"reply": reply})

    except Exception:
        traceback.print_exc()
        return jsonify({"reply": "Errore server"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)