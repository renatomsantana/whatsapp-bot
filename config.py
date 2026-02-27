# =============================================================
# Apenas esse arquivo precisa ser alterado para cada negócio!
# =============================================================

BUSINESS_CONFIG = {
    "name": "Restaurante Sabor Caseiro",
    "type": "restaurante",
    "description": "Restaurante de prato feito, presencial e delivery",
    "hours": "todos os dias das 10h às 15h",
    "services": [
        "Prato feito no salão (presencial)",
        "Delivery de prato feito",
    ],
    "menu_example": [
        "Frango grelhado com arroz, feijão e salada - R$22",
        "Carne assada com macarrão e legumes - R$25",
        "Peixe frito com arroz e pirão - R$28",
        "Opção vegetariana com arroz, feijão e legumes - R$18",
    ],
    "delivery_info": {
        "min_order": 15.00,
        "delivery_fee": 5.00,
        "estimated_time": "40 a 60 minutos",
        "area": "até 5km do restaurante",
    },
    "contact": {
        "address": "Rua das Flores, 123 - Recife, PE",
        "whatsapp": "+5581999999999",
    },
}

# =============================================================
# Configuração dos cupons automáticos
# =============================================================

COUPON_CONFIG = {
    # Quantos dias sem contato para disparar cupom
    "inactive_days": 14,

    # Lista de cupons para enviar em sequência
    "coupons": [
        {
            "days_inactive": 14,
            "message": (
                "Olá, {name}! 😊 Faz um tempinho que você não nos visita...\n\n"
                "Sentimos sua falta! Use o cupom *VOLTA10* e ganhe "
                "*10% de desconto* no seu próximo pedido! 🍽️\n\n"
                "Válido por 7 dias. Estamos abertos todos os dias das 10h às 15h!"
            ),
        },
        {
            "days_inactive": 30,
            "message": (
                "Oi, {name}! 🌟 Há um mês sem novidades suas por aqui...\n\n"
                "Preparamos um presente especial: use *SAUDADE20* e ganhe "
                "*20% de desconto* + *sobremesa grátis*! 🍮\n\n"
                "Corre que é só até domingo!"
            ),
        },
        {
            "days_inactive": 60,
            "message": (
                "Oi, {name}! Já faz 2 meses... 😢\n\n"
                "Renovamos o cardápio e queremos te surpreender!\n"
                "Use *VOLTEI30* e ganhe *30% de desconto* no delivery "
                "ou no salão. Frete grátis também! 🛵✨\n\n"
                "Válido esta semana!"
            ),
        },
    ],
}

# =============================================================
# CONFIGURAÇÃO DA IA (GPT)
# =============================================================

AI_CONFIG = {
    "model": "gpt-4o-mini",  # modelo mais barato e rápido
    "max_tokens": 300,
    "system_prompt": f"""
Você é o assistente virtual do {BUSINESS_CONFIG['name']}.
Você é simpático, objetivo e fala português brasileiro informal.

SOBRE O NEGÓCIO:
- {BUSINESS_CONFIG['description']}
- Horário: {BUSINESS_CONFIG['hours']}
- Endereço: {BUSINESS_CONFIG['contact']['address']}

CARDÁPIO DE HOJE (exemplo):
{chr(10).join(f"- {item}" for item in BUSINESS_CONFIG['menu_example'])}

DELIVERY:
- Pedido mínimo: R${BUSINESS_CONFIG['delivery_info']['min_order']:.2f}
- Taxa de entrega: R${BUSINESS_CONFIG['delivery_info']['delivery_fee']:.2f}
- Tempo estimado: {BUSINESS_CONFIG['delivery_info']['estimated_time']}
- Área de entrega: {BUSINESS_CONFIG['delivery_info']['area']}

REGRAS:
1. Seja sempre simpático e use emojis com moderação
2. Se perguntarem sobre preços, informe os do cardápio
3. Para pedidos de delivery, colete: nome, endereço e itens do pedido
4. Se não souber responder algo, diga que vai verificar e peça para aguardar
5. Não invente informações que não estão acima
""",
}
