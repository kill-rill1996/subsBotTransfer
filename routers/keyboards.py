from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def buy_subscribe_keyboard() -> InlineKeyboardBuilder:
    """Создание клавиатуры для выбора группы"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text="Купить 💸", callback_data="buy_sub"),
        InlineKeyboardButton(text="Статус 🎫", callback_data="sub_status")
                 )
    keyboard.adjust(2)
    return keyboard


def payment_methods(period: str) -> InlineKeyboardBuilder:
    """Клавиатура выбора способа оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Картой (для СНГ)", callback_data=f"pay-method-card_{period}"),
        InlineKeyboardButton(
            text="По ссылке", callback_data=f"pay-method-link_{period}"),
    )
    keyboard.row(InlineKeyboardButton(text="<< Назад", callback_data=f"back-choosePayMethod_{period}"))

    return keyboard


def payment_period_subscribe() -> InlineKeyboardBuilder:
    """Клавиатура для выбора длительности покупаемой подписки"""

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="1 мес", callback_data=f"subPeriod_1"),
        InlineKeyboardButton(
            text="3 мес", callback_data=f"subPeriod_3"),
    )
    keyboard.row(InlineKeyboardButton(
            text="Бессрочная", callback_data=f"subPeriod_inf"))

    keyboard.row(InlineKeyboardButton(text="<< Назад", callback_data="back_menu"))
    return keyboard


def payment_confirm_keyboard(period: str) -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Оплатил", callback_data=f"paid_{period}"),
    )

    keyboard.row(InlineKeyboardButton(text="<< Назад", callback_data="back_choosePayMethod"))
    return keyboard


def admin_payment_confirm_keyboard(payer_tg_id: str, period: str) -> InlineKeyboardBuilder:
    """Клавиатура с кнопкой подтверждения оплаты для админа"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Подтвердить ✅", callback_data=f"admin_ok_{payer_tg_id}_{period}"),
        InlineKeyboardButton(
            text="Отклонить ❌", callback_data=f"admin_cancel_{payer_tg_id}_{period}"),
    )
    return keyboard


def back_to_main_menu() -> InlineKeyboardBuilder:
    """Возвращение на главный экран (аналогично /start)"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="<< Назад", callback_data="back_menu"))
    return keyboard


def invite_link_keyboard(link: str) -> InlineKeyboardBuilder:
    """Клавиатура со ссылкой на вступление в группу"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="🔗 Вступить в группу", url=link))
    return keyboard


