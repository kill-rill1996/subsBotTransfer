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


def create_or_update_operation_and_subscribe(tg_id: str, period: str) -> (tables.Subscription, bool):
    need_link = True

    if period == "1":
        months = settings.months_1
        amount = settings.amount_1
    elif period == "3":
        months = settings.months_3
        amount = settings.amount_3
    else:
        months = settings.months_inf
        amount = settings.amount_inf

    user = db.get_user_by_tg_id(tg_id)

    # получение пользователя с подпиской подписки
    user_with_sub = db.get_user_subscription_by_tg_id(tg_id)

    # создание operations
    operation_model = OperationCreate(
        created_at=datetime.now(pytz.timezone('Europe/Moscow')),
        amount=amount,
        user_id=user.id
    )
    db.create_operation(operation_model)

    if not user_with_sub.subscription:
        # НОВАЯ ПОДПИСКА
        if months == -1:
            is_infinity = True
            expire_date = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30 * 100)
        else:
            is_infinity = False
            expire_date = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30 * months)

        subscription_model = SubscriptionCreate(
            expire_date=expire_date,
            is_active=True,
            user_id=user.id,
            is_infinity=is_infinity
        )
        subscription = db.create_subscription(subscription_model)

    else:
        # ПРОДЛЕНИЕ ПОДПИСКИ
        subscription, need_link = db.update_subscription_expire_date(tg_id, months)

    return subscription, need_link
