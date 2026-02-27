"""
database.py - Gerencia clientes e histórico de conversas
Usa JSON como banco de dados simples (pode trocar por SQLite/PostgreSQL depois)
"""

import json
import os
from datetime import datetime


DB_FILE = "customers.json"


def _load_db() -> dict:
    """Carrega o banco de dados do arquivo JSON."""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(data: dict):
    """Salva o banco de dados no arquivo JSON."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_or_create_customer(phone: str, name: str = None) -> dict:
    """
    Busca um cliente pelo telefone.
    Se não existir, cria um novo registro.
    """
    db = _load_db()

    if phone not in db:
        db[phone] = {
            "phone": phone,
            "name": name or "Cliente",
            "first_contact": datetime.now().isoformat(),
            "last_contact": datetime.now().isoformat(),
            "conversation_history": [],
            "coupons_sent": [],
            "total_messages": 0,
        }
        _save_db(db)
        print(f"[DB] Novo cliente criado: {phone}")

    return db[phone]


def update_last_contact(phone: str):
    """Atualiza a data do último contato do cliente."""
    db = _load_db()
    if phone in db:
        db[phone]["last_contact"] = datetime.now().isoformat()
        db[phone]["total_messages"] += 1
        _save_db(db)


def add_message_to_history(phone: str, role: str, content: str):
    """
    Adiciona uma mensagem ao histórico de conversa.
    role: 'user' ou 'assistant'
    Mantém apenas as últimas 10 mensagens para não gastar tokens demais.
    """
    db = _load_db()
    if phone in db:
        db[phone]["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # Mantém apenas as últimas 10 mensagens
        if len(db[phone]["conversation_history"]) > 10:
            db[phone]["conversation_history"] = db[phone]["conversation_history"][-10:]
        _save_db(db)


def get_conversation_history(phone: str) -> list:
    """Retorna o histórico de conversa no formato que o GPT espera."""
    db = _load_db()
    if phone not in db:
        return []

    # Converte para o formato do GPT (sem o campo timestamp)
    history = []
    for msg in db[phone]["conversation_history"]:
        history.append({
            "role": msg["role"],
            "content": msg["content"],
        })
    return history


def get_inactive_customers(days: int) -> list:
    """
    Retorna clientes que não interagiram há mais de X dias
    e que ainda não receberam cupom para esse período.
    """
    db = _load_db()
    inactive = []

    for phone, customer in db.items():
        last_contact = datetime.fromisoformat(customer["last_contact"])
        days_inactive = (datetime.now() - last_contact).days

        if days_inactive >= days:
            # Verifica se já enviou cupom para esse nível de inatividade
            already_sent = days in customer.get("coupons_sent", [])
            if not already_sent:
                inactive.append({
                    "phone": phone,
                    "name": customer["name"],
                    "days_inactive": days_inactive,
                })

    return inactive


def mark_coupon_sent(phone: str, days_level: int):
    """Marca que um cupom foi enviado para evitar reenvio."""
    db = _load_db()
    if phone in db:
        if days_level not in db[phone]["coupons_sent"]:
            db[phone]["coupons_sent"].append(days_level)
        _save_db(db)


def update_customer_name(phone: str, name: str):
    """Atualiza o nome do cliente."""
    db = _load_db()
    if phone in db:
        db[phone]["name"] = name
        _save_db(db)
