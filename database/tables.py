from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)

    operations = relationship("Operation", back_populates="user", cascade="all, delete")
    subscription = relationship("Subscription", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f'{self.tg_id}. {"@" + self.username if self.username else ""}'


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    amount = Column(Integer, nullable=False)
    is_confirmed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="operations")

    def __repr__(self):
        return f'{self.id}. {self.user_id} {self.amount} {self.created_at}'


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    expire_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_infinity = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f'{self.id}. {self.user_id} {self.is_active} {self.expire_date}'
