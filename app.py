import os
import json
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("AIzaSyBKlJYkWNR-2PzRHzmKWhcK9YONGCvhxjE")

# =========================
# DATABASE SQLITE
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

# =========================
# SALVA MEMORIA
# =========================
def save_memory(user_id, question, answer):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_memory (user_id, question, answer) VALUES (?, ?, ?)",
        (user_id, question, answer)
    )
    conn.commit()
    conn.close()

# =========================
# RECUPERA MEMORIA
# =========================
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
    text = ""
    for k in knowledge:
        text += f"{k['title']}: {k['content']} ({k['url']})\n"
    return text

# =========================
# GEMINI
# =========================
def ask_ai(user_input, user_id):

    history = get_memory(user_id)
    context = build_context()

    prompt = f"""
Sei un assistente umano del sito autoguarizione.it.

COMPORTAMENTO:
- Rispondi in modo naturale
- Non copiare testi
- Aiuta davvero
- Collega le informazioni

STORIA:
{history}

CONTENUTO:
{context}

DOMANDA:
{user_input}

RISPOSTA:
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    r = requests.post(url, json=body)

    if r.status_code != 200:
        return "⚠️ Errore AI"

    data = r.json()

    try:
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        answer = "⚠️ Errore risposta"

    save_memory(user_id, user_input, answer)

    return answer

# =========================
# API CHAT
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    user = request.json.get("message", "")
    user_id = request.json.get("user_id", "default")

    if not user:
        return jsonify({"reply": "Scrivi una domanda 😊"})

    reply = ask_ai(user, user_id)

    return jsonify({"reply": reply})

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "AI + SQLITE ATTIVA"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)