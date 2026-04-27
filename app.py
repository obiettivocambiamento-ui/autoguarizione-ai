import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# MAPPA SEMPLICE DEL SITO
# =========================
SITE_MAP = {
    "home": "https://www.autoguarizione.it/",
    "proposte": "https://www.autoguarizione.it/proposte/",
    "percorso": "https://www.autoguarizione.it/percorso/",
    "analisi": "https://www.autoguarizione.it/analisi/",
    "risorse": "https://www.autoguarizione.it/risorse/",
}

# =========================
# TROVA PAGINA GIUSTA
# =========================
def resolve_url(text):

    t = text.lower()

    for key in SITE_MAP:
        if key in t:
            return SITE_MAP[key]

    return SITE_MAP["home"]

# =========================
# SCARICA E PULISCI PAGINA
# =========================
def fetch_page(url):

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # elimina roba inutile
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # pulizia base
        lines = [l.strip() for l in text.splitlines()]
        clean = "\n".join([l for l in lines if len(l) > 30])

        return clean[:12000]  # limite per Gemini

    except Exception as e:
        print("FETCH ERROR:", e)
        return ""

# =========================
# GEMINI CALL
# =========================
def ask_gemini(context, question):

    if not GEMINI_API_KEY:
        return "API KEY mancante"

    prompt = f"""
Sei un assistente che risponde SOLO usando il contesto del sito.

CONTENUTO DEL SITO:
{context}

DOMANDA UTENTE:
{question}

ISTRUZIONI:
- Rispondi in modo chiaro e naturale
- Non inventare informazioni
- Se il contenuto non basta, dillo chiaramente
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=body, timeout=20)

        if r.status_code != 200:
            print("GEMINI ERROR:", r.text)
            return "Errore AI"

        data = r.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("EXCEPTION:", e)
        return "Errore connessione AI"

# =========================
# CHAT PRINCIPALE
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(force=True)

    text = data.get("message","")

    if not text:
        return jsonify({"reply":"Scrivi qualcosa"})

    # 1. trova pagina
    url = resolve_url(text)

    # 2. legge pagina reale
    content = fetch_page(url)

    # 3. risposta AI
    answer = ask_gemini(content, text)

    return jsonify({
        "reply": answer,
        "source": url
    })

# =========================
@app.route("/")
def home():
    return "AI CHE LEGGE IL SITO ATTIVA"

# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)