import os
import json
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
# CONFIG
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =========================
# DB SQLITE
# =========================
def init_db():
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question TEXT,
            answer TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_memory(user_id, q, a):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_memory (user_id, question, answer) VALUES (?, ?, ?)",
        (user_id, q, a)
    )
    conn.commit()
    conn.close()

def get_memory(user_id):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("""
        SELECT question, answer
        FROM chat_memory
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 5
    """, (user_id,))
    rows = c.fetchall()
    conn.close()

    history = ""
    for q, a in reversed(rows):
        history += f"Utente: {q}\nAI: {a}\n"
    return history

# =========================
# KNOWLEDGE
# =========================
with open("knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

def build_context():
    return "\n".join(
        f"{k['title']}: {k['content']} ({k['url']})"
        for k in knowledge
    )

# =========================
# AI GEMINI (STABILE)
# =========================
def ask_ai(user_input, user_id):

    if not GEMINI_API_KEY:
        return "⚠️ API key mancante"

    history = get_memory(user_id)
    context = build_context()

    prompt = f"""
Sei un assistente del sito autoguarizione.it.

Rispondi in modo naturale, chiaro e utile.

STORIA:
{history}

CONTENUTO SITO:
{context}

DOMANDA:
{user_input}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=body, timeout=15)

        if r.status_code != 200:
            print("GEMINI ERROR:", r.text)
            return "⚠️ AI temporaneamente non disponibile"

        data = r.json()

        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        save_memory(user_id, user_input, answer)

        return answer

    except Exception as e:
        print("EXCEPTION:", str(e))
        return "⚠️ Errore connessione AI"

# =========================
# API CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_input = data.get("message", "")
    user_id = data.get("user_id", "default")

    if not user_input:
        return jsonify({"reply": "Scrivi una domanda"})

    reply = ask_ai(user_input, user_id)

    return jsonify({"reply": reply})

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "AI + SQLITE + GEMINI OK"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)