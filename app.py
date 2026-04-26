from flask import Flask, request, jsonify
import json, os

app = Flask(__name__)

# carica contenuti


with open("data.json","r",encoding="utf-8") as f:
    data = json.load(f)

def search(query):
    results = []
    for chunk in data:
        if any(word in chunk.lower() for word in query.lower().split()):
            results.append(chunk)
    return results[:3]

memory = {}

@app.route("/chat", methods=["POST"])
def chat():
    user = request.json["message"]
    user_id = request.json.get("user_id","default")

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append(user)

    results = search(user)
    context = "\n\n".join(results)

    reply = f"""
Basandomi sul sito:

{context[:500]}

👉 Vuoi approfondire meglio?
"""

    return jsonify({"reply": reply})

@app.route("/")
def home():
    return "AI attiva"

app.run(host="0.0.0.0", port=10000)