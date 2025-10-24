from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(to_whatsapp: str, body: str):
    """
    Envia mensagem via WhatsApp (Twilio), dividindo automaticamente mensagens longas em blocos de até 1600 caracteres.
    """

    # Evita loop: Twilio não permite enviar mensagem do mesmo número para ele mesmo
    if to_whatsapp == TWILIO_WHATSAPP_FROM:
        print(f"Ignorando mensagem: to ({to_whatsapp}) é igual ao from ({TWILIO_WHATSAPP_FROM})")
        return None

    MAX_LEN = 1600
    sid = None

    # Divide o texto em partes de até 1600 caracteres
    partes = [body[i:i+MAX_LEN] for i in range(0, len(body), MAX_LEN)]

    for idx, parte in enumerate(partes):
        # Se houver mais de uma parte, adiciona marcador (1/3), (2/3), etc
        if len(partes) > 1:
            parte = f"({idx+1}/{len(partes)})\n{parte}"

        try:
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_FROM,
                to=to_whatsapp,
                body=parte
            )
            sid = message.sid
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem (parte {idx+1}): {e}")

    return sid
