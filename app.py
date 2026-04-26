from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

app = Flask(__name__)
CORS(app)

# =========================
# CONFIG AI ESTERNA (Gemini)
# =========================
GEMINI_KEY = "INSERISCI_LA_TUA_API_KEY"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-pro:generateContent"
)

# =========================
# CARICA KNOWLEDGE
# =========================
with open("knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [x["text"] for x in data]

vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(texts)


# =========================
# RICERCA LOCALE (VELOCE)
# =========================
def local_search(query):

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix)[0]

    best = scores.argmax()
    score = scores[best]

    if score < 0.25:
        return None

    return texts[best]


# =========================
# AI ESTERNA (FALLBACK INTELLIGENTE)
# =========================
def call_ai(user_message):

    try:
        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ]
        }

        r = requests.post(
            GEMINI_URL + "?key=" + GEMINI_KEY,
            json=payload,
            timeout=20
        )

        data = r.json()

        return (
            data["candidates"][0]["content"]["parts"][0]["text"]
        )

    except Exception as e:
        print("AI ERROR:", e)
        return None


# =========================
# FORMAT RISPOSTA
# =========================
def format_text(text):

    return f"""Ti rispondo in modo chiaro 😊

{text}

Se vuoi posso approfondire meglio."""


# =========================
# CHAT PRINCIPALE
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    user = request.json.get("message", "")

    # 1️⃣ PROVA LOCALE
    local = local_search(user)

    if local:
        return jsonify({
            "reply": format_text(local),
            "source": "local"
        })

    # 2️⃣ PROVA AI
    ai = call_ai(user)

    if ai:
        return jsonify({
            "reply": format_text(ai),
            "source": "ai"
        })

    # 3️⃣ FALLBACK SICURO
    return jsonify({
        "reply": "Non ho trovato una risposta precisa, ma posso aiutarti a riformulare la domanda 😊",
        "source": "fallback"
    })


@app.route("/")
def home():
    return "AI IBRIDA STABILE ATTIVA"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)