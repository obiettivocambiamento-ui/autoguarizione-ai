from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# =========================
# 📦 CARICAMENTO DATI SICURO
# =========================
data = []

if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"data.json caricato: {len(data)} elementi")
    except Exception as e:
        print("Errore caricamento data.json:", e)
        data = []
else:
    print("ATTENZIONE: data.json non trovato")


# =========================
# 🔎 SEARCH SEMPLICE
# =========================
def search(query):
    results = []

    if not data:
        return results

    query_words = query.lower().split()

    for chunk in data:
        text = chunk.lower() if isinstance(chunk, str) else str(chunk).lower()

        if any(word in text for word in query_words):
            results.append(chunk)

        if len(results) >= 3:
            break

    return results


# =========================
# 🧠 MEMORIA CHAT (BASE)
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
# 🚀 START SERVER (Render)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)