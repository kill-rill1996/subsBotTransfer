from datetime import datetime

from database import tables
from settings import settings


def get_help_message() -> str:
    """Help message"""
    message = "<b>Возможности бота:</b>\n" \
              "- Принимает оплату за подписку (по карте (для СНГ) или по ссылке)\n" \
              "- Осуществляет менеджмент приватных каналов/групп\n\n" \
              "<b>Инструкция использования:</b>\n" \
              "- Для перехода в главное меню отправьте команду /menu\n" \
              "- Для покупки или продления подписки в главном меню нажмите \"Купить 💸\"\n" \
              "- Для проверки своего статуса подписки в главном меню нажмите \"Статус 🎫\"\n\n" \
              "<b>Контакт поддержки:</b>\n" \
              f"Если у вас есть вопросы или предложения, свяжитесь с нашей поддержкой в телеграм: {settings.support_contact}"
    return message


def subscription_info(user: tables.User) -> str:
    if not user.subscription:
        return "У вас пока нет подписки, вы можете приобрести ее в главном меню по кнопке \"Купить 💸\""

    message = ""
    expire_date = datetime.strftime(user.subscription[0].expire_date, '%d.%m.%Y')

    if user.subscription[0].is_active:
        if user.subscription[0].is_infinity:
            message += f"🟢 Ваша подписка <b>Активна</b> на <b>неограниченный период</b>"
        else:
            message += f"🟢 Ваша подписка <b>Активна</b> до <b>{expire_date}</b>"
    else:
        message += f"🔴 Срок действия вашей подписки истек <b>{expire_date}</b>\n" \
                   f"Вы можете приобрести подписку в главном меню /menu"

    return message


def get_invoice_message(period: str) -> str:
    message = "Для оплаты подписки на "

    if period == "1":
        message += f"<b>{settings.months_1} месяц</b> "
        amount = f"<b>{settings.amount_1} р.</b>"

    elif period == "3":
        message += f"<b>{settings.months_3} месяца</b> "
        amount = f"<b>{settings.amount_3} р.</b>"

    else:
        message += "<b>неограниченный период</b> "
        amount = f"<b>{settings.amount_inf} р.</b>"

    message += f"необходимо выполнить оплату {amount} по ссылке: \n\n{settings.payment_link}\n\n" \
               f"❗<b>ВАЖНО: в комментарии к оплате для подтверждения платежа необходимо указать при наличии имя пользователя (например @user123) " \
               f"или имя и фамилию, указанные в телеграм</b>\n\n" \
               f"После выполнения оплаты нажмите кнопку <b>\"Оплатил\"</b>"

    return message


def message_for_admin(user: tables.User, period: str) -> str:
    """Оповещение админа об ожидании подтверждения платежа"""
    message = f"Пользователь \nid: {user.tg_id}"
    if user.username:
        message += f"\n@{user.username} "
    if user.firstname:
        message += f"\n{user.firstname} "
    if user.lastname:
        message += f"{user.lastname}"

    if period == "1":
        text = f"<b>{settings.months_1} месяц</b> "
        amount = f"<b>{settings.amount_1} р.</b>"

    elif period == "3":
        text = f"<b>{settings.months_3} месяца</b> "
        amount = f"<b>{settings.amount_3} р.</b>"

    else:
        text = "<b>неограниченный период</b> "
        amount = f"<b>{settings.amount_inf} р.</b>"

    message += f"\nОплатил подписку на {text} стоимостью {amount} \n\nПодтвердите или отклоните оплату"
    return message


def get_waiting_message() -> str:
    message = "Дождитесь подтверждения оплаты администратором, после чего подписка будет активна.\n" \
              "В случае покупки подписки впервые/просрочки подписки вам будет направлена ссылка для вступления в канал"
    return message
