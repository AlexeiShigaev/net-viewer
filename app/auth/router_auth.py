from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from fastapi.responses import JSONResponse

from app.auth.auth import get_password_hash, create_access_token, authenticate_user, get_current_user
from app.auth.schemas import UserData4Auth
from app.database import motorchik

router = APIRouter(prefix="/auth", tags=["Auth API"])


@router.post("/register", summary="Регистрация нового пользователя.")
async def register_new_user(user_data: UserData4Auth, author: UserData4Auth = Depends(get_current_user)) -> dict:
    user = await motorchik.find_one("users", {"login": user_data.login})
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует."
        )

    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    await motorchik.insert_one("users", user_dict)
    return {"result": "Новый пользователь создан."}


@router.post("/change_passwd", summary="Сменить пароль текущего пользователя")
async def change_password(
        response: Response,
        user_data: UserData4Auth,
        author: UserData4Auth = Depends(get_current_user)
) -> dict:

    res = await motorchik.update_one(
        "users",
        find_filter=dict({"login": author["login"]}),
        new_data=dict({"$set": {"password": get_password_hash(user_data.password)}})
    )
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось изменить пароль."
        )
    response.delete_cookie(key="user_access_token")
    print("Изменен пароль для {}.".format(author["login"]))
    return {"result": "Пароль изменен."}


@router.post("/logon", summary="Точка входа")
async def auth_user(response: Response, user_data: UserData4Auth):
    check = await authenticate_user(login=user_data.login, password=user_data.password)
    if check is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Проверьте логин/пароль"
        )
    access_token = create_access_token({"sub": str(check["_id"])})
    response.set_cookie(key="user_access_token", value=access_token)  # , httponly=True
    print("Вход: {}".format(user_data.login))
    return {"access_token": access_token}


@router.get("/me", summary="Проверить авторизован или нет")
async def get_me(user_data: UserData4Auth = Depends(get_current_user)):
    return user_data


@router.get("/logout", summary="Выход")
async def logout_user(response: Response):
    response.delete_cookie(key="user_access_token")
    return {"message": "Пользователь успешно вышел из системы"}
