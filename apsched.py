import datetime

import aiogram
from pytz import timezone

from database import tables, service as db
from settings import settings


async def run_every_day_check(bot: aiogram.Bot):
    """Запуск ежедневной проверки"""
    users = db.get_all_users()
    users_with_subscription = [user for user in users if user.subscription]

    # проверяем активных пользователей
    for user in [user for user in users_with_subscription if user.subscription[0].is_active]:
        # проверяем если истек срок подписки
        if is_sub_expire(user):
            # меняем статус подписки
            db.change_sub_status_to_false(user.id)
            # оповещаем пользователя
            try:
                await notify_user_about_expiration(user.tg_id, bot)
            except:
                pass
            # выгоняем из группы
            await kick_user_from_channel(int(user.tg_id), bot)


def is_sub_expire(user: tables.User) -> bool:
    """Проверка истечения срока подписки"""
    if user.subscription[0].expire_date.date() < datetime.datetime.now(tz=timezone('Europe/Moscow')).date():
        return True
    return False


async def kick_user_from_channel(user_tg_id: int, bot: aiogram.Bot):
    """Удаление пользователя из канала"""
    await bot.ban_chat_member(settings.channel_id, user_tg_id)
    await bot.unban_chat_member(settings.channel_id, user_tg_id)


async def notify_user_about_expiration(user_tg_id: int, bot: aiogram.Bot):
    """Оповещение пользователя об окончании подписки"""
    await bot.send_message(user_tg_id, "Ваша подписка закончилась, вы можете приобрести подписку в главном меню /menu")

