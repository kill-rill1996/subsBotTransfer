from datetime import datetime

import aiogram
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from middleware import CheckPrivateMessageMiddleware
from database import service as db

from database.models import UserCreate
from .payments import create_payment_invoice
from .utils import is_user_exists, create_or_update_operation_and_subscribe, generate_invite_link
from routers import messages as ms, keyboards as kb
from settings import settings

router = Router()
router.message.middleware.register(CheckPrivateMessageMiddleware())


# BLOCK OTHER TYPES
@router.message(~F.content_type.in_({'text', 'pre_checkout_query', 'successful_payment'}))
async def block_types_handler(message: types.Message) -> None:
    await message.answer("Некорректный тип данных в сообщении (принимается только текст)\n\n"
                         "Чтобы посмотреть инструкцию по использованию бота выберите команду /help во вкладке \"Меню\" "
                         "или нажмите на команду прямо в сообщении")


@router.message(Command("start"))
async def start_message(message: types.Message) -> None:
    """Команда /start"""
    if not is_user_exists(str(message.from_user.id)):
        user_model = UserCreate(
            tg_id=str(message.from_user.id),
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name
        )
        db.create_user(user_model)

    await message.answer("Вы можете приобрести или продлить подписку на канал", reply_markup=kb.buy_subscribe_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data == "back_menu")
@router.message(Command("menu"))
async def main_menu(message: types.Message | types.CallbackQuery) -> None:
    if type(message) == types.Message:
        await message.answer("Вы можете приобрести или продлить подписку на канал",
                             reply_markup=kb.buy_subscribe_keyboard().as_markup())
    else:
        await message.message.edit_text("Вы можете приобрести или продлить подписку на канал",
                             reply_markup=kb.buy_subscribe_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data == "buy_sub")
@router.callback_query(lambda callback: callback.data == "back-choosePeriod")
async def buy_menu(callback: types.CallbackQuery) -> None:
    """Меню выбора периода подписки"""
    await callback.message.edit_text("Выберите период подписки 🗓", reply_markup=kb.payment_period_subscribe().as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "subPeriod")
@router.callback_query(lambda callback: callback.data.split("_")[0] == "back-choosePayMethod")
async def choose_buy_method(callback: types.CallbackQuery) -> None:
    """Меню выбора способа оплаты подписки"""
    period = callback.data.split("_")[1]
    await callback.message.edit_text("Выберите способ оплаты", reply_markup=kb.payment_methods(period).as_markup())


# ОПЛАТА КАРТОЙ
@router.callback_query(lambda callback: callback.data.split('_')[0] == "pay-method-card")
async def create_invoice_handler(callback: types.CallbackQuery) -> None:
    """Формирование заказа для оплаты"""
    period = callback.data.split("_")[1]
    payment_invoice = create_payment_invoice(period)

    await callback.message.answer_invoice(**payment_invoice)
    await callback.message.delete()


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: types.Message, bot: aiogram.Bot):
    """В случае успешной оплаты по карте"""
    payer_tg_id = str(message.from_user.id)
    amount = int(message.successful_payment.invoice_payload)
    if amount == settings.amount_1:
        months = settings.months_1
    elif amount == settings.amount_3:
        months = settings.months_3
    else:
        months = settings.months_inf

    # создание и продление подписки
    subscription, need_link = create_or_update_operation_and_subscribe(payer_tg_id, months, amount)

    if need_link:
        # создание invite ссылки
        name = message.from_user.username if message.from_user.username else message.from_user.first_name
        invite_link = await generate_invite_link(bot, name)

        # для бессрочной подписки
        if subscription.is_infinity:
            user_message = f"Оплата прошла успешно ✅\nПодписка активна на <b>неограниченный период</b>️ ♾️\n\n" \
                           "<b>Ссылка на вступление в канал активна 1 день и может быть использована только 1 раз</b>"
        # для обычной подписки
        else:
            user_message = f"Оплата прошла успешно ✅\nПодписка активна до <b>{datetime.strftime(subscription.expire_date, '%d.%m.%Y')}</b> 🗓️\n\n" \
                           "<b>Ссылка на вступление в канал активна 1 день и может быть использована только 1 раз</b>"

        # отправка ссылки пользователю
        await message.answer(user_message, reply_markup=kb.invite_link_keyboard(invite_link).as_markup())

    # без ссылки (в случае продления активной подписки)
    else:
        # для бессрочной подписки
        if subscription.is_infinity:
            user_message = f"Оплата прошла успешно ✅\nПодписка активна на <b>неограниченный период</b> ♾️️"

        # для обычной подписки
        else:
            user_message = f"Оплата прошла успешно ✅\nПодписка активна до <b>{datetime.strftime(subscription.expire_date, '%d.%m.%Y')}</b> 🗓️"

        # отправка сообщения пользователю без ссылки (т.к. его подписка еще активна и он в канале)
        await message.answer(user_message)


# ОПЛАТА ПО ССЫЛКЕ
@router.callback_query(lambda callback: callback.data.split('_')[0] == "pay-method-link")
async def create_invoice_handler_link(callback: types.CallbackQuery) -> None:
    """Формирование заказа для оплаты"""
    sub_period = callback.data.split("_")[1]
    invoice_message = ms.get_invoice_message(sub_period)

    await callback.message.edit_text(invoice_message, reply_markup=kb.payment_confirm_keyboard(sub_period).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == "paid")
async def waiting_message_handler(callback: types.CallbackQuery, bot: aiogram.Bot) -> None:
    """Ожидание подтверждения от админа"""
    # убираем кнопки в предыдущем сообщении
    period = callback.data.split("_")[1]
    invoice_message = ms.get_invoice_message(period)
    await callback.message.edit_text(invoice_message)

    # оповещаем администратора
    tg_id = str(callback.from_user.id)
    user = db.get_user_by_tg_id(tg_id)
    message_to_admin = ms.message_for_admin(user, period)
    await bot.send_message(settings.admins[0],
                           message_to_admin,
                           reply_markup=kb.admin_payment_confirm_keyboard(tg_id, period).as_markup())

    # отправка сообщения пользователю с просьбой дождаться подтверждения админа
    message = ms.get_waiting_message()
    await callback.message.answer(message)


@router.callback_query(lambda callback: callback.data == "sub_status")
async def check_sub_status(callback: types.CallbackQuery):
    """Проверка своей подписки"""
    tg_id = callback.from_user.id
    user = db.get_user_subscription_by_tg_id(str(tg_id))
    msg = ms.subscription_info(user)

    await callback.message.edit_text(msg, reply_markup=kb.back_to_main_menu().as_markup())


@router.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    """Help message"""
    msg = ms.get_help_message()
    await message.answer(msg)


