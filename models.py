from enum import Enum as PyEnum
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Boolean, Text, String, ForeignKey, DECIMAL, UniqueConstraint, Enum

from database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class Order(Base):
    ORDER_STATUSES = (
        ("PENDING", "pending"),
        ("IN-TRANSIT", "in-transit"),
        ("DELIVERED", "delivered"),
    )
    PIZZA_SIZES = (
        ("SMALL", "small"),
        ("MEDIUM", "medium"),
        ("LARGE", "large"),
        ("EXTRA-LARGE", "extra-large"),
    )

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default="PENDING")
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES), default="SMALL")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="orders")
    payments = relationship("DBPayment", back_populates="order")


    def __repr__(self):
        return f"<Order {self.id}>"


class PaymentStatus(PyEnum):
    PENDING = "PENDING"
    PAID = "PAID"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class DBPayment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    order_id = Column(Integer, ForeignKey("orders.id"))
    session_url = Column(String(1023))
    session_id = Column(String(500))
    money_to_pay = Column(DECIMAL(precision=8, scale=2))

    order = relationship("Order", back_populates="payments")


