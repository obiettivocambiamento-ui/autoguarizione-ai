from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = Flask(__name__)
CORS(app)

# =========================
# CARICAMENTO KNOWLEDGE
# =========================
with open("knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [item["text"] for item in data]

# =========================
# STOPWORDS ITALIANE BASE (COMPATIBILI)
# =========================
ITALIAN_STOPWORDS = [
    "il", "lo", "la", "i", "gli", "le",
    "un", "una", "e", "o", "di", "da", "a",
    "che", "come", "cosa", "per", "con",
    "su", "nel", "nella", "nei", "nelle",
    "è", "sono", "era", "essere", "ho", "hai"
]

# =========================
# MODELLO TF-IDF
# =========================
vectorizer = TfidfVectorizer(stop_words=ITALIAN_STOPWORDS)
matrix = vectorizer.fit_transform(texts)

# =========================
# MATCH SEMANTICO
# =========================
def find_best_match(query):
    if not query:
        return None

    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix)[0]

    best_index = scores.argmax()
    best_score = scores[best_index]

    # soglia anti-risposte casuali
    if best_score < 0.12:
        return None

    return data[best_index]

# =========================
# RISPOSTA PULITA
# =========================
def build_response(item):
    return f"""📌 {item['title']}

{item['text']}

🔗 Approfondisci:
{item['url']}
"""

# =========================
# API CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")

        item = find_best_match(user_message)

        if item is None:
            return jsonify({
                "reply": "Non ho trovato una sezione precisa nel sito. Puoi riformulare la domanda?"
            })

        return jsonify({
            "reply": build_response(item),
            "source": item["id"]
        })

    except Exception as e:
        return jsonify({
            "reply": "Errore interno del server."
        }), 500

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "AI SEMANTICA ATTIVA - OK"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)