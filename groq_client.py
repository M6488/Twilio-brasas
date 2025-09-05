import requests
from config import GROQ_API_KEY, GROQ_MODEL

_GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def gerar_resposta(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        resp = requests.post(_GROQ_ENDPOINT, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERRO na IA]: {str(e)}"
