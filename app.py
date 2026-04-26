from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)

# =========================
# 🌐 CORS (OBBLIGATORIO PER WORDPRESS)
# =========================
CORS(app)

# =========================
# 📦 CARICAMENTO DATA.JSON
# =========================
data = []

if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"data.json caricato: {len(data)} elementi")
    except Exception as e:
        print("Errore data.json:", e)
        data = []
else:
    print("ATTENZIONE: data.json non trovato")


# =========================
# 🔎 SEARCH (VERSIONE STABILE)
# =========================
def search(query):
    results = []

    query = query.lower()

    for chunk in data:
        text = chunk.lower() if isinstance(chunk, str) else str(chunk).lower()

        score = 0
        for word in query.split():
            if word in text:
                score += 1

        if score > 0:
            results.append((score, chunk))

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:3]]


# =========================
# 🧠 MEMORIA CHAT
# =========================
memory = {}


# =========================
# 💬 CHAT API
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        req = request.get_json()

        if not req or "message" not in req:
            return jsonify({"reply": "Messaggio non valido"}), 400

        user = req["message"]
        user_id = req.get("user_id", "default")

        if user_id not in memory:
            memory[user_id] = []

        memory[user_id].append(user)

        results = search(user)

        context = "\n\n".join(results) if results else "Nessun contenuto trovato nel sito."

        reply = f"""
Basandomi sui contenuti del sito:

{context[:800]}

👉 Vuoi approfondire meglio?
"""

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Errore server: {str(e)}"}), 500


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "AI attiva"


# =========================
# 🚀 START SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)