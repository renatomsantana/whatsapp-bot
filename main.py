"""
main.py - Webhook Flask que recebe mensagens do WhatsApp via Twilio

Como funciona:
1. Cliente manda mensagem no WhatsApp
2. Twilio recebe e faz POST para /webhook
3. Flask processa e responde
4. Twilio entrega a resposta para o cliente
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import bot
import database as db

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint que o Twilio chama quando chega uma mensagem.
    O Twilio envia os dados como form-data.
    """

    # Pega os dados da mensagem enviados pelo Twilio
    incoming_msg = request.form.get("Body", "").strip()
    sender_phone = request.form.get("From", "")  # formato: whatsapp:+5581999999999
    profile_name = request.form.get("ProfileName", "Cliente")

    print(f"[WEBHOOK] Mensagem de {sender_phone}: {incoming_msg}")

    # Garante que o cliente existe no banco
    customer = db.get_or_create_customer(sender_phone, profile_name)

    # Tenta extrair o nome se o cliente ainda não tem nome personalizado
    if customer["name"] == "Cliente":
        extracted_name = bot.extract_name_from_message(incoming_msg)
        if extracted_name:
            db.update_customer_name(sender_phone, extracted_name)
            print(f"[WEBHOOK] Nome extraído: {extracted_name}")

    # Pega a resposta do GPT
    reply = bot.get_bot_response(sender_phone, incoming_msg)

    # Monta a resposta no formato que o Twilio espera (TwiML)
    response = MessagingResponse()
    response.message(reply)

    print(f"[WEBHOOK] Resposta enviada: {reply[:50]}...")
    return str(response)


@app.route("/health", methods=["GET"])
def health():
    """Endpoint para verificar se o servidor está rodando."""
    return {"status": "ok", "message": "Bot está rodando! 🤖"}, 200


if __name__ == "__main__":
    print("🤖 Bot do WhatsApp iniciado!")
    print("📡 Webhook disponível em: http://localhost:5000/webhook")
    app.run(debug=True, port=5000)
