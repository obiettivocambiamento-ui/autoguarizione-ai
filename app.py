import os
import json
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =====================
# LOAD KNOWLEDGE
# =====================
with open("knowledge.json", "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# =====================
# MEMORY SQLITE
# =====================
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

def save(user_id, q, a):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat (user_id,q,a) VALUES (?,?,?)", (user_id,q,a))
    conn.commit()
    conn.close()

def history(user_id):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("SELECT q,a FROM chat WHERE user_id=? ORDER BY id DESC LIMIT 3", (user_id,))
    rows = c.fetchall()
    conn.close()
    return " ".join([q+" "+a for q,a in rows])

# =====================
# INTENT MATCHING (SEMANTICO BASE)
# =====================
def find_knowledge(text):

    t = text.lower()

    for item in KNOWLEDGE:
        for k in item["keywords"]:
            if k in t:
                return item

    return None

# =====================
# GEMINI (SOLO REWRITE)
# =====================
def refine_with_gemini(text, base_answer):

    if not GEMINI_API_KEY:
        return base_answer

    prompt = f"""
Rendi questa risposta più naturale e fluida senza cambiare il significato:

RISPOSTA BASE:
{base_answer}

DOMANDA UTENTE:
{text}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [{"parts":[{"text":prompt}]}]
    }

    try:
        r = requests.post(url, json=body, timeout=10)

        if r.status_code != 200:
            return base_answer

        data = r.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except:
        return base_answer

# =====================
# CHAT ENGINE
# =====================
def generate_answer(text, user_id):

    item = find_knowledge(text)

    if item:
        base = item["answer"]

        final = refine_with_gemini(text, base)

        save(user_id, text, final)

        return final + f"\n\n🔗 {item['url']}"

    # fallback intelligente
    return "Puoi chiedere di proposte, percorsi, analisi o risorse del sito."

# =====================
# API CHAT
# =====================
@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(force=True)

        text = data.get("message", "")
        user_id = data.get("user_id", "u1")

        if not text.strip():
            return jsonify({"reply": "Scrivi una domanda"})

        reply = generate_answer(text, user_id)

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Errore sistema"}), 200

# =====================
# HOME
# =====================
@app.route("/")
def home():
    return "AI SEMANTICA FINALE OK"

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)