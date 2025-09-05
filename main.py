from fastapi import FastAPI, HTTPException
from db import fetch_one, fetch_all, execute
from twilio_client import enviar_mensagem
from groq_client import gerar_resposta
from nordeste import nordestinizar
import uuid

app = FastAPI(title="Brasas - Sistema de Pedidos")

# ------------------------------
# CLIENTES
# ------------------------------
@app.post("/clientes")
def criar_cliente(nome: str, telefone: str, email: str):
    query = "INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s) RETURNING id"
    cliente = fetch_one(query, (nome, telefone, email))
    return {"id": cliente["id"], "mensagem": "Cliente cadastrado com sucesso"}

# ------------------------------
# CARDÁPIO
# ------------------------------
@app.get("/cardapio")
def listar_cardapio():
    return fetch_all("SELECT * FROM cardapio WHERE ativo = TRUE")

# ------------------------------
# CARRINHO
# ------------------------------
@app.post("/carrinho/{cliente_id}")
def criar_carrinho(cliente_id: int):
    query = "INSERT INTO carrinhos (usuario_id, status) VALUES (%s, 'aberto') RETURNING id"
    carrinho = fetch_one(query, (cliente_id,))
    return {"carrinho_id": carrinho["id"]}

@app.post("/carrinho/{carrinho_id}/adicionar")
def adicionar_item(carrinho_id: str, produto_id: int, quantidade: int):
    execute(
        "INSERT INTO itens_carrinho (carrinho_id, produto_id, quantidade) VALUES (%s, %s, %s) ON CONFLICT (carrinho_id, produto_id) DO UPDATE SET quantidade = itens_carrinho.quantidade + EXCLUDED.quantidade",
        (carrinho_id, produto_id, quantidade),
    )
    return {"mensagem": "Produto adicionado ao carrinho"}

@app.post("/carrinho/{carrinho_id}/remover")
def remover_item(carrinho_id: str, produto_id: int):
    execute("DELETE FROM itens_carrinho WHERE carrinho_id=%s AND produto_id=%s", (carrinho_id, produto_id))
    return {"mensagem": "Produto removido do carrinho"}

@app.post("/carrinho/{carrinho_id}/finalizar")
def finalizar_carrinho(carrinho_id: str, tipo_pagamento: str = "pix"):
    # Fecha carrinho
    execute("UPDATE carrinhos SET status='fechado', finalizado_em=now() WHERE id=%s", (carrinho_id,))

    # Cria pagamento fictício
    pagamento_id = str(uuid.uuid4())
    execute(
        "INSERT INTO pagamentos (id, carrinho_id, tipo_pagamento, status, dados_brutos) VALUES (%s, %s, %s, %s, %s)",
        (pagamento_id, carrinho_id, tipo_pagamento, "concluido", '{"simulacao":"pagamento aprovado"}'),
    )

    return {"mensagem": "Carrinho finalizado e pagamento aprovado", "pagamento_id": pagamento_id}

# ------------------------------
# IA
# ------------------------------
@app.get("/ia/pergunta")
def perguntar_ia(pergunta: str):
    resposta = gerar_resposta(pergunta)
    return {"resposta": nordestinizar(resposta)}

# ------------------------------
# TWILIO
# ------------------------------
@app.post("/enviar_mensagem")
def enviar_msg(destino: str, mensagem: str):
    return enviar_mensagem(destino, mensagem)
