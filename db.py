import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Tuple
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def fetch_one(query: str, params: Tuple=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

def fetch_all(query: str, params: Tuple=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def execute(query: str, params: Tuple=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()

def get_or_create_cliente_por_telefone(telefone: str, nome: Optional[str]=None, email: Optional[str]=None):
    cli = fetch_one("SELECT * FROM clientes WHERE telefone = %s", (telefone,))
    if cli:
        return cli
    return fetch_one(
        "INSERT INTO clientes (telefone, nome, email) VALUES (%s,%s,%s) RETURNING *",
        (telefone, nome, email)
    )


def listar_cardapio_ativo():
    return fetch_all("SELECT id, nome, preco_centavos, descricao FROM cardapio WHERE ativo = TRUE ORDER BY nome")

def buscar_produto_por_nome(nome: str):
    return fetch_one("SELECT id, nome, preco_centavos FROM cardapio WHERE ativo = TRUE AND LOWER(nome) LIKE %s LIMIT 1",
                     (f"%{nome.lower()}%",))


def get_or_create_carrinho_aberto(cliente_id: int):
    carr = fetch_one("SELECT * FROM carrinhos WHERE usuario_id=%s AND status='aberto' ORDER BY criado_em DESC LIMIT 1", (cliente_id,))
    if carr:
        return carr
    return fetch_one("INSERT INTO carrinhos (usuario_id, status) VALUES (%s,'aberto') RETURNING *", (cliente_id,))

def add_item(carrinho_id, produto_id, quantidade: int):
    execute(
        """INSERT INTO itens_carrinho (carrinho_id, produto_id, quantidade)
            VALUES (%s,%s,%s)
            ON CONFLICT (carrinho_id, produto_id)
            DO UPDATE SET quantidade = itens_carrinho.quantidade + EXCLUDED.quantidade""",\
        (carrinho_id, produto_id, quantidade)
    )

def remove_item(carrinho_id, produto_id):
    execute("DELETE FROM itens_carrinho WHERE carrinho_id=%s AND produto_id=%s", (carrinho_id, produto_id))

def listar_itens_carrinho(carrinho_id):
    return fetch_all(
        """SELECT ic.produto_id, c.nome, c.preco_centavos, ic.quantidade, (c.preco_centavos * ic.quantidade) AS subtotal
            FROM itens_carrinho ic
            JOIN cardapio c ON c.id = ic.produto_id
            WHERE ic.carrinho_id = %s
            ORDER BY c.nome""", (carrinho_id,)
    )

def total_carrinho_centavos(carrinho_id) -> int:
    res = fetch_one("""SELECT COALESCE(SUM(c.preco_centavos * ic.quantidade),0) AS total
                         FROM itens_carrinho ic
                         JOIN cardapio c ON c.id = ic.produto_id
                         WHERE ic.carrinho_id=%s""", (carrinho_id,))
    return int(res["total"] or 0)


def finalizar_carrinho_e_criar_pedido(cliente_id, carrinho_id):
    carr = fetch_one("UPDATE carrinhos SET status='fechado', finalizado_em=now() WHERE id=%s RETURNING *", (carrinho_id,))
    ped = fetch_one("INSERT INTO pedidos (cliente_id, carrinho_id, status) VALUES (%s,%s,'aguardando_pagamento') RETURNING *",
                    (cliente_id, carrinho_id))
    return ped

def criar_pagamento_ficticio(carrinho_id, tipo: str):
    pg = fetch_one(
        "INSERT INTO pagamentos (carrinho_id, tipo_pagamento, status, dados_brutos) VALUES (%s,%s,'pendente','{\"mock\":true}') RETURNING *",
        (carrinho_id, tipo)
    )

    pg = fetch_one("UPDATE pagamentos SET status='concluido' WHERE id=%s RETURNING *", (pg["id"],))
    ped = fetch_one("UPDATE pedidos SET status='concluido', atualizado_em=now() WHERE carrinho_id=%s RETURNING *", (carrinho_id,))
    return pg, ped