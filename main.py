from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any
from config import TWILIO_WHATSAPP_FROM
from twilio_client import send_whatsapp
import db
from nordeste import nordestinizar
from groq_client import nlu_intencao

app = FastAPI(title="Chatbot Restaurante")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/cardapio")
def http_cardapio():
    return db.listar_cardapio_ativo()

@app.get("/carrinho/{telefone}")
def http_carrinho(telefone: str):
    cli = db.get_or_create_cliente_por_telefone(telefone)
    carr = db.get_or_create_carrinho_aberto(cli["id"])
    itens = db.listar_itens_carrinho(carr["id"])
    total = db.total_carrinho_centavos(carr["id"]) / 100
    return {"carrinho_id": carr["id"], "itens": itens, "total": total}

@app.post("/twilio/webhook", response_class=PlainTextResponse)
async def twilio_webhook(request: Request):
    form = await request.form()
    
    from_number = form.get("From")      
    body = (form.get("Body") or "").strip()
    profile_name = form.get("ProfileName") or None

    telefone = from_number.replace("whatsapp:", "") if from_number else ""
    cliente = db.get_or_create_cliente_por_telefone(telefone, nome=profile_name)
    carrinho = db.get_or_create_carrinho_aberto(cliente["id"])

    intent = nlu_intencao(body)

    if intent["acao"] == "saudacao":
        resposta = saudacao(cliente.get("nome") or "cliente")

    elif intent["acao"] == "cardapio":
        resposta = montar_cardapio_texto()

    elif intent["acao"] == "listar_carrinho":
        resposta = montar_carrinho_texto(carrinho["id"])

    elif intent["acao"] == "adicionar":
        adicionados = []
        for item in intent.get("itens", []):
            prod = db.buscar_produto_por_nome(item.get("nome",""))
            if prod:
                qtd = max(1, int(item.get("quantidade") or 1))
                db.add_item(carrinho["id"], prod["id"], qtd)
                adicionados.append(f"{qtd}x {prod['nome']}")
        if adicionados:
            resposta = f"Botei no carrinho: {', '.join(adicionados)}. Quer ver o carrinho ou finalizar?"
        else:
            resposta = "Num achei esses itens no cardápio não, visse? Diz de novo o nome certinho."

    elif intent["acao"] == "remover":
        removidos = []
        for item in intent.get("itens", []):
            prod = db.buscar_produto_por_nome(item.get("nome",""))
            if prod:
                db.remove_item(carrinho["id"], prod["id"])
                removidos.append(prod["nome"])
        if removidos:
            itens_restantes = db.listar_itens_carrinho(carrinho["id"])
            if itens_restantes:
                linhas = [f"{i['quantidade']}x {i['nome']}" for i in itens_restantes]
                resposta = (
                    f"Tirei do carrinho: {', '.join(removidos)}. "
                    f"Ainda ficou com: {', '.join(linhas)}."
                )
            else:
                resposta = f"Tirei do carrinho: {', '.join(removidos)}. Agora teu carrinho tá vazio."
        else:
            resposta = "Num encontrei esses itens no carrinho, meu rei."

    elif intent["acao"] == "finalizar":
        pedido = db.finalizar_carrinho_e_criar_pedido(cliente["id"], carrinho["id"])
        pagamento, pedido_atual = db.criar_pagamento_ficticio(carrinho["id"], "pix")
        total = db.total_carrinho_centavos(carrinho["id"]) / 100
        resposta = f"Pedido {pedido_atual['id']} finalizado! Total R$ {total:.2f}. Pagamento aprovado ✅. Já já sai quentinho!"

    else:
        resposta = "Posso te mostrar o cardápio, adicionar itens ao carrinho, remover, listar ou finalizar. Como te ajudo?"

    resposta = nordestinizar(resposta)

    if from_number:
        to_whatsapp = f"whatsapp:{telefone}"
        send_whatsapp(to_whatsapp, resposta)

    return


def saudacao(nome: str):
    return f"Bem-vindo ao Brasas, {nome}! Quer ver nosso cardápio?"

def montar_cardapio_texto():
    itens = db.listar_cardapio_ativo()
    if not itens:
        return "Vixe, o cardápio tá vazio por enquanto."
    linhas = []
    for it in itens:
        preco = float(it['preco_real']) if it['preco_real'] is not None else 0.0
        desc = f" — {it['descricao']}" if it.get('descricao') else ""
        linhas.append(f"- {it['nome']} — R$ {preco:.2f}{desc}")
    return "Cardápio de hoje:\n" + "\n".join(linhas) + "\n\nPeça assim: 'quero 2 x-burgers e 1 coca'."


def montar_carrinho_texto(carrinho_id):
    itens = db.listar_itens_carrinho(carrinho_id)
    if not itens:
        return "Teu carrinho tá vazio, cabra. Quer ver o cardápio?"

    linhas = [f"{i['quantidade']}x {i['nome']} = R$ {float(i['subtotal']):.2f}" for i in itens]
    total = db.total_carrinho_reais(carrinho_id)
    return "Teu carrinho:\n" + "\n".join(linhas) + f"\nTotal: R$ {total:.2f}\nDiz 'finalizar' pra fechar o pedido."