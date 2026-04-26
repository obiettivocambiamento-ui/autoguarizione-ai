from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# =========================
# 📦 CARICAMENTO ROBUSTO DATA
# =========================
data = []

if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            raw = json.load(f)

        # 🔥 FORZA TUTTO A STRINGA
        if isinstance(raw, list):
            data = [str(x) for x in raw]
        elif isinstance(raw, dict):
            data = [str(v) for v in raw.values()]
        else:
            data = [str(raw)]

        print("DATA CARICATO OK:", len(data))

    except Exception as e:
        print("ERRORE DATA.JSON:", e)
        data = []
else:
    print("data.json mancante")


# =========================
# 🔎 SEARCH SICURA (NO CRASH)
# =========================
def search(query):
    if not data:
        return []

    query = (query or "").lower()

    results = []

    for chunk in data:
        try:
            text = str(chunk).lower()

            score = sum(1 for w in query.split() if w in text)

            if score > 0:
                results.append((score, chunk))

        except:
            continue

    results.sort(reverse=True, key=lambda x: x[0])

    return [r[1] for r in results[:3]]


# =========================
# 💬 CHAT (ULTRA SAFE)
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        req = request.get_json(silent=True)

        if not req:
            return jsonify({"reply": "Errore: richiesta non valida"}), 400

        user = req.get("message", "")

        results = search(user)

        context = "\n\n".join(results) if results else "Nessun contenuto trovato."

        return jsonify({
            "reply": f"Basandomi sul sito:\n\n{context[:800]}"
        })

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Errore server interno"}), 500


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "AI attiva"


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)