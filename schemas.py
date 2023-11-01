from pydantic import BaseModel
from typing import Optional

from models import PaymentStatus


class SignUp(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "Mao",
                "email": "hi@ki.com",
                "password": "password",
                "is_staff": False,
                "is_active": True,
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = (
        "072d9fdf88351f2e5473db45daa7cc83f181ecc60947d8d8b73d24eb03535f4d"
    )


class LoginModel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = "PENDING"
    pizza_size: Optional[str] = "SMALL"
    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "pizza_size": "LARGE",
            }
        }


class OrderStatusModel(BaseModel):

    order_status: Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING",
            }
        }


class PaymentModel(BaseModel):
    id: Optional[int]
    status: Optional[str] = "PENDING"
    order_id: Optional[int]
    session_url: Optional[str]
    session_id: Optional[str]
    money_to_pay: Optional[float]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "status": "PENDING",
                "order_id": 3,
            }
        }