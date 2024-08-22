from pydantic import BaseModel, Field


class UserData4Auth(BaseModel):
    login: str = Field(..., min_length=1, description="Имя пользователя.")
    password: str = Field(..., min_length=3, max_length=50, description="Пароль, от 3 до 50 знаков")


