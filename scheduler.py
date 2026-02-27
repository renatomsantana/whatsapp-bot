"""
scheduler.py - Job que roda automaticamente e envia cupons para clientes inativos

Como funciona:
1. A cada hora verifica o banco de dados
2. Encontra clientes que não interagem há X dias
3. Envia mensagem personalizada com cupom
4. Marca que o cupom foi enviado (não envia duplicado)
"""

import schedule
import time
from twilio.rest import Client
from config import COUPON_CONFIG, BUSINESS_CONFIG
import database as db
import os


# Pega as credenciais do Twilio das variáveis de ambiente
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # formato: whatsapp:+14155238886


def send_whatsapp_message(to_phone: str, message: str) -> bool:
    """
    Envia uma mensagem WhatsApp via Twilio.
    Retorna True se enviou com sucesso, False se falhou.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_phone,
            body=message,
        )
        print(f"[SCHEDULER] Mensagem enviada para {to_phone}")
        return True

    except Exception as e:
        print(f"[SCHEDULER] Erro ao enviar para {to_phone}: {e}")
        return False


def check_and_send_coupons():
    """
    Função principal do scheduler.
    Verifica clientes inativos e envia cupons.
    """
    print("[SCHEDULER] Verificando clientes inativos...")

    for coupon in COUPON_CONFIG["coupons"]:
        days_inactive = coupon["days_inactive"]
        inactive_customers = db.get_inactive_customers(days_inactive)

        if not inactive_customers:
            print(f"[SCHEDULER] Nenhum cliente inativo há {days_inactive} dias.")
            continue

        print(f"[SCHEDULER] {len(inactive_customers)} clientes inativos há {days_inactive} dias.")

        for customer in inactive_customers:
            # Personaliza a mensagem com o nome do cliente
            message = coupon["message"].format(
                name=customer["name"],
                business_name=BUSINESS_CONFIG["name"],
            )

            success = send_whatsapp_message(customer["phone"], message)

            if success:
                # Marca que esse cupom foi enviado para não reenviar
                db.mark_coupon_sent(customer["phone"], days_inactive)


def start_scheduler():
    """Inicia o agendador de tarefas."""
    print("[SCHEDULER] Iniciando agendador de cupons...")

    # Roda a verificação a cada hora
    schedule.every(1).hour.do(check_and_send_coupons)

    # Roda uma vez imediatamente ao iniciar
    check_and_send_coupons()

    print("[SCHEDULER] Agendador rodando! Verificação a cada hora.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # verifica a cada minuto se tem tarefa pendente


if __name__ == "__main__":
    start_scheduler()
