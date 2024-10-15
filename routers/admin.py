from datetime import datetime

import aiogram
import requests
from aiogram import Router, types
from aiogram.filters import Command

from middleware import CheckIsAdminMiddleware, CheckPrivateMessageMiddleware
from settings import settings
import routers.keyboards as kb
from routers.utils import create_operation_and_subscribe, create_invite_link

router = Router()
router.message.middleware.register(CheckPrivateMessageMiddleware())
router.message.middleware.register(CheckIsAdminMiddleware(settings.admins))


@router.callback_query(lambda callback: callback.data.split('_')[0] == "admin")
async def create_invoice_handler(callback: types.CallbackQuery, bot: aiogram.Bot) -> None:
    """Вывод результата оплаты"""
    payer_tg_id = callback.data.split("_")[2]
    period = callback.data.split("_")[3]
    payment_status = callback.data.split("_")[1]

    if payment_status == "ok":
        subscription = create_operation_and_subscribe(payer_tg_id, period)
        invite_link = create_invite_link(payer_tg_id, bot)

        user_message =f"Оплата прошла успешно ✅\nПодписка активна до <b>{datetime.strftime(subscription.expire_date, '%d.%m.%Y')}</b> 🗓️\n\n"\
                      "<b>Ссылка на вступление в канал активна 1 день и может быть использована только 1 раз</b>"

        await bot.send_message(payer_tg_id, user_message, reply_markup=kb.invite_link_keyboard(invite_link).as_markup())

        admin_message = "Оплата подтверждена ✅\nСсылка на вступление направлена пользователю"  # сообщение админу

    else:
        user_message = "Администратора оплату не подтвердил ❌"
        await bot.send_message(payer_tg_id, user_message)

        admin_message = "Оплата отклонена ❌\nОповещение направлено пользователю"

    # оповещение админа
    await callback.message.edit_text(admin_message)

