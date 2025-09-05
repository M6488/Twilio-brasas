import requests
import json
import re
from config import GROQ_API_KEY, GROQ_MODEL

_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def nlu_intencao(texto: str) -> dict:
    """
    Extrai a intenção do usuário e itens do pedido.
    Saída esperada:
    {
      "acao": "cardapio|adicionar|remover|listar_carrinho|finalizar|saudacao|desconhecido",
      "itens": [{"nome": "hamburguer", "quantidade": 2}, ...]
    }
    """
    if not GROQ_API_KEY:
        lower = texto.lower()
        if any(k in lower for k in ["cardapio","cardápio","menu"]):
            return {"acao":"cardapio","itens":[]}
        if any(k in lower for k in ["finalizar","fechar pedido","pagar"]):
            return {"acao":"finalizar","itens":[]}
        if any(k in lower for k in ["meu carrinho","carrinho","itens"]):
            return {"acao":"listar_carrinho","itens":[]}
        if any(k in lower for k in ["oi","olá","ola","bom dia","boa tarde","boa noite"]):
            return {"acao":"saudacao","itens":[]}
        if "remover" in lower or "tirar" in lower:
            nome_item = lower.replace("remover","").replace("tirar","").strip()
            return {"acao":"remover","itens":[{"nome": nome_item, "quantidade":1}]}
        if "quero" in lower or "add " in lower:
            toks = lower.split()
            qtd = 1
            try:
                qtd = int([t for t in toks if t.isdigit()][0])
            except:
                pass
            nome_item = lower.replace("quero","").replace("add","").strip()
            return {"acao":"adicionar","itens":[{"nome": nome_item, "quantidade": qtd}]}
        return {"acao":"desconhecido","itens":[]}

    # Uso do GROQ API
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    # Prompt com JSON de exemplo sem usar f-string dentro do JSON
    prompt = f"""Você é um NLU de pedidos de restaurante. Extraia a intenção e itens do texto a seguir e responda SOMENTE JSON válido.

TEXTO: {texto}

Saída JSON com as chaves:
- acao: cardapio | adicionar | remover | listar_carrinho | finalizar | saudacao | desconhecido
- itens: lista com objetos {{nome, quantidade}} quando fizer sentido

Exemplos:
"quero 2 x-burgers e 1 coca" => {{"acao":"adicionar","itens":[{{"nome":"x-burger","quantidade":2}},{{"nome":"coca","quantidade":1}}]}}
"remover coca" => {{"acao":"remover","itens":[{{"nome":"coca","quantidade":1}}]}}
"meu carrinho" => {{"acao":"listar_carrinho","itens":[]}}
"finalizar" => {{"acao":"finalizar","itens":[]}}
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role":"system","content":"Responda apenas JSON válido."},
            {"role":"user","content": prompt}
        ],
        "temperature": 0.1
    }

    try:
        r = requests.post(_ENDPOINT, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]

        
        m = re.search(r'\{[\s\S]*\}', content)
        if m:
            return json.loads(m.group(0))

        return {"acao":"desconhecido","itens":[]}
    except Exception:
        return {"acao":"desconhecido","itens":[]}
