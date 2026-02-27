"""
bot.py - Lógica de conversa com GPT
Recebe a mensagem do cliente e retorna a resposta da IA
"""

from openai import OpenAI
from config import AI_CONFIG
import database as db


client = OpenAI()  # usa a variável de ambiente OPENAI_API_KEY automaticamente


def get_bot_response(phone: str, user_message: str) -> str:
    """
    Processa a mensagem do cliente e retorna resposta do GPT.
    
    Fluxo:
    1. Busca/cria cliente no banco
    2. Salva mensagem do usuário no histórico
    3. Manda histórico + mensagem para o GPT
    4. Salva resposta do GPT no histórico
    5. Retorna resposta
    """

    # 1. Atualiza o registro do cliente
    db.get_or_create_customer(phone)
    db.update_last_contact(phone)

    # 2. Salva mensagem do usuário
    db.add_message_to_history(phone, "user", user_message)

    # 3. Busca histórico para dar contexto ao GPT
    history = db.get_conversation_history(phone)

    # 4. Monta a requisição para o GPT
    messages = [
        {"role": "system", "content": AI_CONFIG["system_prompt"]}
    ] + history  # histórico já inclui a mensagem atual

    try:
        response = client.chat.completions.create(
            model=AI_CONFIG["model"],
            messages=messages,
            max_tokens=AI_CONFIG["max_tokens"],
        )
        bot_reply = response.choices[0].message.content

    except Exception as e:
        print(f"[BOT] Erro ao chamar GPT: {e}")
        bot_reply = (
            "Desculpe, tive um probleminha aqui! 😅 "
            "Por favor, tente novamente em alguns instantes."
        )

    # 5. Salva resposta do bot no histórico
    db.add_message_to_history(phone, "assistant", bot_reply)

    return bot_reply


def extract_name_from_message(message: str) -> str | None:
    """
    Tenta extrair o nome do cliente da mensagem.
    Exemplo: 'Oi, meu nome é João' -> 'João'
    Simples por enquanto, pode melhorar com regex ou NLP depois.
    """
    message_lower = message.lower()
    triggers = ["meu nome é ", "me chamo ", "sou o ", "sou a "]

    for trigger in triggers:
        if trigger in message_lower:
            idx = message_lower.index(trigger) + len(trigger)
            name = message[idx:].split()[0].strip(".,!?")
            return name.capitalize()

    return None
