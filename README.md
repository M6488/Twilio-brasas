# 🤖 Chatbot de Restaurante (WhatsApp + FastAPI + Twilio)

Este projeto implementa um **chatbot inteligente para o restaurante Brasas**, que se comunica via **WhatsApp** utilizando a API do **Twilio**, processa mensagens com **IA (Groq)** e gerencia pedidos em um banco de dados **PostgreSQL**.

---

## 📋 Funcionalidades

- Envio automático de mensagens via **Twilio WhatsApp API**
- Entendimento de **intenção de linguagem natural** (saudação, pedido, cardápio, remoção, finalização)
- Consulta dinâmica ao **cardápio do banco de dados**
- Agrupamento de bebidas alcoólicas sob a categoria **“Alcoólicas”**
- Divisão automática de mensagens em blocos de até **1600 caracteres**
- Controle completo de **carrinho de compras**
- Finalização de pedidos com **simulação de pagamento**
- Respostas com tom regionalizado (função `nordestinizar`)

---

## 🧱 Estrutura do Projeto

📦 chatbot_restaurante/
├── main.py
├── db.py
├── twilio_client.py
├── groq_client.py
├── nordeste.py
├── config.py
└── requirements.txt


---

## ⚙️ Configuração

Crie um arquivo `.env` com suas credenciais:

DATABASE_URL=postgresql://usuario:senha@host:5432/nome_banco
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GROQ_API_KEY=sua_chave_groq

| Comando do Usuário               | Ação do Chatbot                                     |
| -------------------------------- | --------------------------------------------------- |
| “Oi”, “Olá”, “E aí”              | Envia saudação personalizada                        |
| “Quero ver o cardápio”           | Mostra o cardápio completo, dividido por categorias |
| “Adicionar 2 x-burgers e 1 coca” | Adiciona itens ao carrinho                          |
| “Remover 1 coca”                 | Remove itens do carrinho                            |
| “Ver carrinho”                   | Lista os itens atuais e total                       |
| “Finalizar pedido”               | Finaliza e simula pagamento                         |


📋 *Cardápio de Hoje*

🥪 *Sandubas*
1. X-Burger — R$ 24.90
2. X-Bacon — R$ 27.50

🍷 *Alcoólicas*
1. Cerveja Heineken — R$ 12.00
2. Vinho Tinto — R$ 35.00

👉 Peça assim: "quero 2 x-burgers e 1 coca"

🧾 Licença

Este projeto é open-source sob licença MIT.

👨‍💻 Desenvolvido por Lucas Santiago Andion Gradin
💬 IA com sotaque nordestino powered by Groq + FastAPI + Twilio
