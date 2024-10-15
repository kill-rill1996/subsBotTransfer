from datetime import datetime, timedelta

import pytz
from sqlalchemy.orm import joinedload

from database import tables
from .database import Session
from .models import UserCreate, OperationCreate, User, SubscriptionCreate


# USER
def create_user(user_model: UserCreate) -> tables.User:
    """Добавление пользователя"""
    with Session() as session:
        user = tables.User(**user_model.dict())
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user_by_id(user_id: int) -> tables.User:
    """Получение юзера по id"""
    with Session() as session:
        user = session.query(tables.User) \
            .filter(tables.User.id == user_id) \
            .first()
        return user


def get_user_by_tg_id(tg_id: str) -> tables.User:
    """Получение юзера по tg_id"""
    with Session() as session:
        user = session.query(tables.User) \
            .filter(tables.User.tg_id == tg_id) \
            .first()
        return user


def delete_user(user_id: int) -> None:
    """Удаление юзера по id"""
    with Session() as session:
        user = get_user_by_tg_id(str(user_id))
        session.delete(user)
        session.commit()


# OPERATION
def create_operation(operation_model: OperationCreate) -> tables.Operation:
    """Добавление операции"""
    with Session() as session:
        operation = tables.Operation(**operation_model.dict())
        session.add(operation)
        session.commit()
        session.refresh(operation)
        return operation


# SUBSCRIPTION
def create_subscription(subscription_model: SubscriptionCreate) -> tables.Subscription:
    """Создание подписки"""
    with Session() as session:
        subscription = tables.Subscription(**subscription_model.dict())
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
        return subscription


def get_user_subscription_by_tg_id(tg_id: str) -> tables.User:
    """Получение подписки по id пользователя"""
    with Session() as session:
        user = session.query(tables.User).filter(tables.User.tg_id == tg_id)\
            .options(joinedload(tables.User.subscription)).first()
        return user


def get_all_users() -> list[tables.User]:
    """Все пользователи"""
    with Session() as session:
        users = session.query(tables.User).options(joinedload(tables.User.subscription))
        return users


def change_sub_status_to_false(user_id: int):
    """Меняет статус подписки на false"""
    with Session() as session:
        subscription = session.query(tables.Subscription).filter_by(user_id=user_id).first()
        subscription.is_active = False
        session.commit()


def get_subscription_by_user_id(user_id: int) -> tables.Subscription:
    """Получение подписки по id пользователя"""
    with Session() as session:
        subscription = session.query(tables.Subscription).\
            filter(tables.Subscription.user_id == user_id).\
            first()
        return subscription


def update_subscription_expire_date(tg_id: str, months: int) -> datetime.date:
    """Обновление срока подписки"""
    user_with_sub = get_user_subscription_by_tg_id(tg_id)
    current_expire_date = user_with_sub.subscription[0].expire_date

    # если подписка уже кончилась
    if current_expire_date.replace(tzinfo=pytz.timezone('Europe/Moscow')) < datetime.now(pytz.timezone('Europe/Moscow')):
        new_expire_date = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30 * months)
    # если подписка еще активна
    else:
        new_expire_date = current_expire_date + timedelta(days=30 * months)

    # продление
    with Session() as session:
        subscription = session.query(tables.Subscription).filter_by(user_id=user_with_sub.id).first()
        subscription.expire_date = new_expire_date
        subscription.is_active = True
        session.commit()

    return new_expire_date
