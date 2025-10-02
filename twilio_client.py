from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(to_whatsapp: str, body: str):
    
    if to_whatsapp == TWILIO_WHATSAPP_FROM:
        print(f"Ignorando mensagem: to ({to_whatsapp}) é igual ao from ({TWILIO_WHATSAPP_FROM})")
        return None

    message = client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=to_whatsapp,
        body=body
    )
    return message.sid