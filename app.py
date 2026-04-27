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
# MODELLI DA PROVARE
# =========================
GEMINI_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-pro"
]

@app.route("/")
def home():
    return "OK - SERVER ATTIVO"

# =========================
# GEMINI CALL ROBUSTA
# =========================
def call_gemini(message):

    if not GEMINI_API_KEY:
        return "Errore AI (API key mancante)"

    last_error = None

    for model in GEMINI_MODELS:

        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/"
                f"models/{model}:generateContent?key={GEMINI_API_KEY}"
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

            print(f"📦 MODELLO: {model}")
            print("📦 RAW:", data)

            if "error" in data:
                last_error = data["error"].get("message")
                continue

            if "candidates" not in data or len(data["candidates"]) == 0:
                last_error = "candidates vuoti"
                continue

            candidate = data["candidates"][0]

            if "content" not in candidate:
                last_error = "no content"
                continue

            return candidate["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"🔥 ERRORE MODELLO {model}")
            traceback.print_exc()
            last_error = str(e)

    return f"Errore Gemini: nessun modello valido. Ultimo errore: {last_error}"


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