from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_mensagem(destino: str, mensagem: str):
    """Envia mensagem WhatsApp ou SMS usando Twilio"""
    try:
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            to=destino,
            body=mensagem
        )
        return {"status": "sucesso", "sid": message.sid}
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}
