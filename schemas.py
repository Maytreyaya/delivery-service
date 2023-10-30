from pydantic import BaseModel
from typing import Optional


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
            'example': {
                'username': 'Mao',
                'email': 'hi@ki.com',
                'password': 'password',
                'is_staff': False,
                'is_active': True,
            }
        }


class Settings(BaseModel):
    authjwt_secret_key:str = '072d9fdf88351f2e5473db45daa7cc83f181ecc60947d8d8b73d24eb03535f4d'


class LoginModel(BaseModel):
    username: str
    password: str
