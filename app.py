import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("🚀 SERVER STARTING...")

# =========================
# GEMINI API KEY
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("🔑 GEMINI KEY PRESENTE:", bool(GEMINI_API_KEY))

# =========================
# HOME TEST
# =========================
@app.route("/")
def home():
    return "OK - SERVER ATTIVO"

# =========================
# GEMINI CALL SAFE
# =========================
def call_gemini(message):

    if not GEMINI_API_KEY:
        return "Errore AI (Gemini non disponibile: API key mancante)"

    try:
        import requests

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

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

        if response.status_code != 200:
            print("❌ GEMINI ERROR STATUS:", response.status_code)
            print(response.text)
            return "Errore AI (Gemini risposta non valida)"

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("🔥 GEMINI EXCEPTION")
        traceback.print_exc()
        return "Errore AI interno"

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

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        print("🔥 CHAT ERROR")
        traceback.print_exc()

        return jsonify({
            "reply": "Errore server interno"
        }), 200

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":

    try:
        app.run(host="0.0.0.0", port=10000)

    except Exception as e:
        print("💥 FATAL ERROR")
        traceback.print_exc()