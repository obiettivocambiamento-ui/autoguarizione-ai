import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

print("🚀 SERVER STARTING...")

# =========================
# GEMINI SAFE INIT
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI API KEY MANCANTE (ma server parte lo stesso)")

# =========================
# SAFE CHAT FUNCTION
# =========================
def call_gemini_safe(text):

    try:
        if not GEMINI_API_KEY:
            return "AI non configurata (API key mancante)"

        import requests

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

        payload = {
            "contents": [
                {"parts": [{"text": text}]}
            ]
        }

        r = requests.post(url, json=payload, timeout=20)

        if r.status_code != 200:
            print("GEMINI ERROR:", r.text)
            return "Errore AI (Gemini non disponibile)"

        data = r.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("GEMINI EXCEPTION:", e)
        return "Errore AI interno"

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "OK - AI SERVER STABILE ATTIVO"

# =========================
# CHAT (ROBUSTA)
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(force=True)
        text = data.get("message", "")

        if not text:
            return jsonify({"reply": "scrivi un messaggio"})

        reply = call_gemini_safe(text)

        return jsonify({"reply": reply})

    except Exception as e:
        print("🔥 CHAT CRASH:")
        traceback.print_exc()

        return jsonify({
            "reply": "Errore server (debug attivo)"
        }), 200

# =========================
# START SAFE
# =========================
if __name__ == "__main__":

    try:
        print("✅ Flask starting...")
        app.run(host="0.0.0.0", port=10000)

    except Exception as e:
        print("💥 FATAL:", e)
        traceback.print_exc()