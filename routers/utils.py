from datetime import datetime, timedelta
import pytz
import aiogram

from database import service as db, tables
from database.models import OperationCreate, SubscriptionCreate
from settings import settings


def is_user_exists(user_tg_id: str) -> bool:
    """Проверяет есть ли уже такой user в базе данных"""
    user = db.get_user_by_tg_id(user_tg_id)
    if user:
        return True
    return False


async def generate_invite_link(bot: aiogram.Bot, name: str) -> str:
    """Создание ссылки для подписки на группу"""
    # время окончание действия ссылки на вступление
    expire_date = datetime.now(tz=pytz.timezone('Europe/Moscow')) + timedelta(days=1)

    invite_link = await bot.create_chat_invite_link(chat_id=settings.channel_id,
                                                    name=name,
                                                    expire_date=int(expire_date.timestamp()),
                                                    member_limit=1)
    return invite_link.invite_link


async def create_invite_link(tg_id: str, bot: aiogram.Bot) -> str:
    user = db.get_user_by_tg_id(tg_id)

    link_name = user.username if user.username else user.first_name
    invite_link = await generate_invite_link(bot, link_name)
    return invite_link


def create_operation_and_subscribe(tg_id: str, period: str) -> tables.Subscription:
    if period == "1":
        months = 1
        amount = 100
    elif period == "3":
        months = 3
        amount = 300
    else:
        months = -1
        amount = 1000

    user = db.get_user_by_tg_id(tg_id)

    # создание operations
    operation_model = OperationCreate(
        created_at=datetime.now(pytz.timezone('Europe/Moscow')),
        amount=amount,
        user_id=user.id
    )
    db.create_operation(operation_model)

    # создание subscription
    user_with_sub = db.get_user_subscription_by_tg_id(tg_id)

    # получение ссылки на подписку
    # name = message.from_user.username if message.from_user.username else message.from_user.first_name
    # invite_link = await generate_invite_link(bot, name)

    # продление подписки
    if user_with_sub.subscription:
        subscription = db.update_subscription_expire_date(tg_id, months)    # TODO исправить чтобы subcription

    # создание подписки
    else:
        # создание подписки
        expire_date = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30 * months)
        subscription_model = SubscriptionCreate(
            expire_date=expire_date,
            is_active=True,
            user_id=user.id
        )
        subscription = db.create_subscription(subscription_model)

    return subscription
