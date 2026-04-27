import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# memoria conversazione
chat_history = []

def call_gemini(prompt):

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()

        if "error" in data:
            return f"❌ Errore Gemini: {data['error'].get('message')}"

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Errore server: {str(e)}"


def chat(message, history):

    global chat_history

    # costruzione memoria
    context = ""
    for h in chat_history[-5:]:
        context += f"Utente: {h['user']}\nAI: {h['ai']}\n"

    prompt = f"""
Sei un assistente intelligente che risponde in modo chiaro, utile e concreto.

Conversazione:
{context}

Nuova domanda:
{message}

Risposta:
"""

    response = call_gemini(prompt)

    chat_history.append({
        "user": message,
        "ai": response
    })

    return response


demo = gr.ChatInterface(
    fn=chat,
    title="🔥 Autoguarizione AI",
    description="AI conversazionale con memoria + Gemini"
)

demo.launch()