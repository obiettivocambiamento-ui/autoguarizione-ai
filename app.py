import os
import json
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

with open("knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# =========================
# MEMORY
# =========================
def init_db():
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            q TEXT,
            a TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def history(user_id):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("SELECT q,a FROM chat WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    rows = c.fetchall()
    conn.close()
    return "\n".join([f"U:{q}\nA:{a}" for q,a in rows])

# =========================
# GEMINI CALL (VERO RAG)
# =========================
def ask_gemini(prompt):

    if not GEMINI_API_KEY:
        raise Exception("NO API KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {"parts":[{"text":prompt}]}
        ]
    }

    r = requests.post(url, json=body, timeout=15)

    if r.status_code != 200:
        print("GEMINI ERROR:", r.text)
        raise Exception("Gemini failed")

    data = r.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

# =========================
# SEMANTIC SEARCH (NON KEYWORD)
# =========================
def search_knowledge(user_text):

    t = user_text.lower()

    best = None
    score = 0

    for item in KNOWLEDGE:

        s = 0

        for k in item["keywords"]:
            if k in t:
                s += 1

        if s > score:
            score = s
            best = item

    return best

# =========================
# CORE AI LOGIC
# =========================
def generate(user_text, user_id):

    context = search_knowledge(user_text)

    base_context = ""
    link = ""

    if context:
        base_context = context["answer"]
        link = context["url"]

    prompt = f"""
Sei un assistente AI avanzato.

CONTESTO SITO:
{base_context}

STORIA:
{history(user_id)}

UTENTE:
{user_text}

REGOLE:
- Rispondi in modo naturale
- Usa il contesto solo se utile
- Non ripetere frasi del contesto
- Se serve, spiega meglio
"""

    try:
        answer = ask_gemini(prompt)

        if link:
            answer += f"\n\n🔗 {link}"

        return answer

    except Exception as e:
        print("AI ERROR:", e)

        # fallback minimo MA intelligente
        if context:
            return context["answer"] + f"\n\n🔗 {context['url']}"

        return "Non riesco a generare risposta al momento."

# =========================
# API
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(force=True)

    text = data.get("message","")
    user_id = data.get("user_id","u1")

    if not text:
        return jsonify({"reply":"Scrivi qualcosa"})

    reply = generate(text, user_id)

    return jsonify({"reply": reply})

# =========================
@app.route("/")
def home():
    return "AI SEMANTICA + GEMINI ATTIVA"

# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)