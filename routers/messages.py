from datetime import datetime

from database import tables
from settings import settings


def get_help_message() -> str:
    """Help message"""
    message = "<b>Возможности бота:</b>\n" \
              "- Принимает оплату за подписку\n" \
              "- Осуществляет менеджмент приватных каналов/групп\n\n" \
              "<b>Инструкция использования:</b>\n" \
              "- Для начала работы отправьте команду /start и следуйте инструкциям\n" \
              "- Для перехода в главное меню отправьте команду /menu\n" \
              "- Для покупки или продления подписки в главном меню нажмите \"Купить 💸\"\n" \
              "- Для проверки своего статуса подписки в главном меню нажмите \"Статус 🎫\"\n\n" \
              "<b>Контакт поддержки:</b>\n" \
              "Если у вас есть вопросы или предложения, свяжитесь с нашей поддержкой в телеграм: @aleksandr_andreew"
    return message


def subscription_info(user: tables.User) -> str:
    if not user.subscription:
        return "У вас пока нет подписки, вы можете приобрести ее в главном меню по кнопке \"Купить 💸\""

    message = ""
    expire_date = datetime.strftime(user.subscription[0].expire_date, '%d.%m.%Y')

    if user.subscription[0].is_active:
        message += f"🟢 Ваша подписка <b>Активна</b> до <b>{expire_date}</b>"
    else:
        message += f"🔴 Срок действия вашей подписки истек <b>{expire_date}</b>\n" \
                   f"Вы можете приобрести подписку в главном меню /start"

    return message


def get_invoice_message(period: str) -> str:
    message = "Для оплаты подписки на "

    if period == "1":
        message += "<b>1 месяц</b> "
        amount = "<b>100 р.</b>"

    elif period == "3":
        message += "<b>3 месяца</b> "
        amount = "<b>300 р.</b>"

    else:
        message += "<b>неограниченный период</b> "
        amount = "<b>1000 р.</b>"

    message += f"необходимо выполнить перевод по ссылке \n{settings.payment_link}\nна сумму {amount}\n\n" \
               f"После выполнения оплаты нажмите кнопку <b>\"Оплатил\"</b>"

    return message


def message_for_admin(user: tables.User, period: str) -> str:
    """Оповещение админа об ожидании подтверждения платежа"""
    message = f"Пользователь id: {user.tg_id} "
    if user.username:
        message += f"@{user.username} "
    if user.firstname:
        message += f"{user.firstname} "
    if user.lastname:
        message += f"{user.lastname} "

    if period == "1":
        text = "<b>1 месяц</b> "
        amount = "<b>100 р.</b>"

    elif period == "3":
        text = "<b>3 месяца</b> "
        amount = "<b>300 р.</b>"

    else:
        text = "<b>неограниченный период</b> "
        amount = "<b>1000 р.</b>"

    message += f"оплатил подписку на {text} стоимостью {amount} \n\nПроверьте или отклоните оплату"


def get_waiting_message() -> str:
    message = "Дождитесь подтверждения оплаты администратором, после вам будет направлена ссылка для вступления в канал"
    return message
