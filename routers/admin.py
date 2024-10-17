from datetime import datetime

import aiogram
from aiogram import Router, types, F

from middleware import CheckIsAdminMiddleware, CheckPrivateMessageMiddleware
from settings import settings
from database import service as db
import routers.keyboards as kb
from routers.utils import create_or_update_operation_and_subscribe, generate_invite_link

router = Router()
router.message.middleware.register(CheckPrivateMessageMiddleware())
router.message.middleware.register(CheckIsAdminMiddleware(settings.admins))


# BLOCK OTHER TYPES
@router.message(~F.content_type.in_({'text', 'pre_checkout_query', 'successful_payment'}))
async def block_types_handler(message: types.Message) -> None:
    await message.answer("Некорректный тип данных в сообщении (принимается только текст)\n\n"
                         "Чтобы посмотреть инструкцию по использованию бота выберите команду /help во вкладке \"Меню\" "
                         "или нажмите на команду прямо в сообщении")


@router.callback_query(lambda callback: callback.data.split('_')[0] == "admin")
async def create_invoice_handler(callback: types.CallbackQuery, bot: aiogram.Bot) -> None:
    """Вывод результата оплаты"""
    payer_tg_id = callback.data.split("_")[2]
    period = callback.data.split("_")[3]
    payment_status = callback.data.split("_")[1]

    if period == "1":
        months = settings.months_1
        amount = settings.amount_1
    elif period == "3":
        months = settings.months_3
        amount = settings.amount_3
    else:
        months = settings.months_inf
        amount = settings.amount_inf

    # ПОДТВЕРЖДЕНИЕ ОПЛАТЫ
    if payment_status == "ok":
        # создание и продление подписки
        subscription, need_link = create_or_update_operation_and_subscribe(payer_tg_id, months, amount)

        # создание ссылки (в случае новой подписки или продления истекшей подписки)
        if need_link:
            # создание invite ссылки
            name = callback.message.from_user.username if callback.message.from_user.username else callback.message.from_user.first_name
            invite_link = await generate_invite_link(bot, name)

            # для бессрочной подписки
            if subscription.is_infinity:
                user_message = f"Оплата прошла успешно ✅\nПодписка активна на <b>неограниченный период</b>️ ♾️\n\n" \
                               "<b>Ссылка на вступление в канал активна 1 день и может быть использована только 1 раз</b>"
            # для обычной подписки
            else:
                user_message = f"Оплата прошла успешно ✅\nПодписка активна до <b>{datetime.strftime(subscription.expire_date, '%d.%m.%Y')}</b> 🗓️\n\n"\
                               "<b>Ссылка на вступление в канал активна 1 день и может быть использована только 1 раз</b>"

            # отправка ссылки пользователю
            await bot.send_message(payer_tg_id, user_message, reply_markup=kb.invite_link_keyboard(invite_link).as_markup())

            # сообщение админу
            admin_message = f"Оплата подтверждена ✅\nСсылка на вступление направлена пользователю"

        # без ссылки (в случае продления активной подписки)
        else:
            # для бессрочной подписки
            if subscription.is_infinity:
                user_message = f"Оплата прошла успешно ✅\nПодписка активна на <b>неограниченный период</b>️ ♾️"

            # для обычной подписки
            else:
                user_message = f"Оплата прошла успешно ✅\nПодписка активна до <b>{datetime.strftime(subscription.expire_date, '%d.%m.%Y')}</b> 🗓️"

            # отправка сообщения пользователю без ссылки (т.к. его подписка еще активна и он в канале)
            await bot.send_message(payer_tg_id, user_message)

            # сообщение админу
            admin_message = "Оплата подтверждена ✅\nПодписка пользователя продлена"

    # ОТКЛОНЕНИЕ ОПЛАТЫ
    else:
        # сообщение пользователю
        user_message = f"Администратора оплату не подтвердил ❌\n\n" \
                       f"Вы можете связаться с администрацией канала\n{settings.support_contact}"
        await bot.send_message(payer_tg_id, user_message)

        # сообщение админу
        admin_message = "Оплата отклонена ❌\nОповещение направлено пользователю"

    # оповещение админа
    await callback.message.edit_text(callback.message.text)
    await callback.message.answer(admin_message)

