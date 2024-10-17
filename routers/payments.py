from aiogram.types import LabeledPrice

from settings import settings


def create_payment_invoice(sub_period: str) -> dict:
    # для неограниченного периода
    if sub_period == "inf":
        description = f"Оплата подписки на неограниченный период"
        label = "Неограниченный период"
        amount = settings.amount_inf
    # для 1 и 3 месяцев
    else:
        label = sub_period
        description = f"Оплата подписки на {sub_period}"
        # 1 месяц
        if sub_period == str(settings.months_1):
            label += " месяц"
            description += " месяц"
            amount = settings.amount_1
        # 3 месяца
        else:
            label += " месяца"
            description += " месяца"
            amount = settings.amount_3

    payment_invoice = {
        "title": "Подписка на канал",
        "description": description,
        "payload": f"{amount}",
        "currency": "RUB", "provider_token": settings.payment_token,
        "prices": [LabeledPrice(label=label, amount=amount * 100)],
        "protect_content": True,
        "photo_url": "https://www.searchenginejournal.com/wp-content/uploads/2020/03/the-top-10-most-popular-online-payment-solutions-5e9978d564973.png"
    }

    return payment_invoice