from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    tg_id: str
    username: str | None
    firstname: str | None
    lastname: str | None


class User(UserCreate):
    id: int


class OperationCreate(BaseModel):
    created_at: datetime
    amount: int
    user_id: int


class SubscriptionCreate(BaseModel):
    user_id: int
    expire_date: datetime
    is_active: bool
