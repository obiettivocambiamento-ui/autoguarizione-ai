import os
import sqlite3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# =====================
# DB SQLITE
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
    c.execute("INSERT INTO chat (user_id, q, a) VALUES (?,?,?)",
              (user_id, q, a))
    conn.commit()
    conn.close()

def history(user_id):
    conn = sqlite3.connect("memory.db")
    c = conn.cursor()
    c.execute("SELECT q,a FROM chat WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    rows = c.fetchall()
    conn.close()

    return "\n".join([f"U:{q}\nA:{a}" for q,a in reversed(rows)])

# =====================
# GEMINI
# =====================
def ask_ai(text, user_id):

    if not GEMINI_API_KEY:
        return "API KEY mancante"

    prompt = f"""
Sei un assistente chiaro e naturale.

STORIA:
{history(user_id)}

DOMANDA:
{text}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        r = requests.post(url, json=body, timeout=15)

        if r.status_code != 200:
            print("GEMINI ERROR:", r.text)
            return "AI temporaneamente non disponibile"

        data = r.json()

        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        save(user_id, text, answer)

        return answer

    except Exception as e:
        print("ERROR:", e)
        return "Errore AI"

# =====================
# CHAT API (FIX DEFINITIVO)
# =====================
@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(force=True)

        text = data.get("message", "")
        user_id = data.get("user_id", "u1")

        if not text:
            return jsonify({"reply": "Scrivi qualcosa"})

        reply = ask_ai(text, user_id)

        return jsonify({"reply": reply})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Errore server"}), 500

# =====================
# HOME
# =====================
@app.route("/")
def home():
    return "AI + SQLITE + GEMINI OK"

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)