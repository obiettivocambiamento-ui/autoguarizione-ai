import os
import traceback
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("🚀 SERVER STARTING...")

# =========================
# GEMINI KEY
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("🔑 GEMINI KEY PRESENTE:", bool(GEMINI_API_KEY))

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "OK - SERVER ATTIVO"

# =========================
# GEMINI FUNCTION (STABILE)
# =========================
def call_gemini(message):

    if not GEMINI_API_KEY:
        return "Errore AI (API key mancante)"

    try:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": message}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload, timeout=20)

        # 🔥 DEBUG RAW
        data = response.json()
        print("📦 GEMINI RAW RESPONSE:", data)

        # ❌ errore API
        if "error" in data:
            return f"Errore Gemini API: {data['error'].get('message', 'unknown')}"

        # ❌ risposta vuota
        if "candidates" not in data or len(data["candidates"]) == 0:
            return "Gemini non ha generato risposta (vuoto o blocco)"

        candidate = data["candidates"][0]

        # ❌ struttura non valida
        if "content" not in candidate:
            return "Risposta Gemini non valida (struttura inattesa)"

        return candidate["content"]["parts"][0]["text"]

    except Exception as e:
        print("🔥 GEMINI EXCEPTION")
        traceback.print_exc()
        return "Errore interno AI"

# =========================
# CHAT ENDPOINT
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
        print("🔥 CHAT ERROR")
        traceback.print_exc()

        return jsonify({"reply": "Errore server"}), 200

# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)