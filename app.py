from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

# =========================
# CARICA DATI (non più centrale)
# =========================
data = []

if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)


# =========================
# 🧠 INTELLIGENZA BASE (QUI CAMBIA TUTTO)
# =========================
def ai_brain(user):

    u = user.lower()

    # 👉 COME FUNZIONA IL SITO
    if "come funziona" in u:
        return """Il sito è pensato per aiutarti in un percorso di autoguarigione.

Offre strumenti, contenuti e percorsi per aumentare la consapevolezza, migliorare la salute e comprendere meglio te stesso.

Puoi esplorare diverse aree come nutrizione, respirazione, energia e crescita personale."""

    # 👉 PROPOSTE
    if "proposte" in u:
        return """Le proposte del sito includono diversi percorsi e strumenti pratici.

Tra questi ci sono:
- percorsi di crescita personale
- strumenti di analisi
- contenuti per migliorare salute e consapevolezza
- risorse pratiche da applicare nella vita quotidiana"""

    # 👉 RISORSE
    if "risorse" in u:
        return """Il sito offre varie risorse utili per il tuo percorso.

Ad esempio:
- guide pratiche
- strumenti operativi
- contenuti di approfondimento
- materiali per lavorare su corpo e mente"""

    # 👉 DEFAULT (usa contenuto sito ma filtrato)
    return """Sto ancora imparando dai contenuti del sito.

Prova a chiedermi:
- come funziona il sito
- quali sono le proposte
- quali risorse offre

👉 Posso aiutarti a orientarti meglio."""


# =========================
# CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():
    try:
        req = request.get_json()
        user = req.get("message", "")

        reply = ai_brain(user)

        return jsonify({"reply": reply})

    except:
        return jsonify({"reply": "Errore interno"}), 500


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "AI attiva"


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)