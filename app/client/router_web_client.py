from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates

from app.auth.auth import get_current_user, get_token


router = APIRouter(prefix="/web", tags=["web-client"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, summary="Страница для авторизации")
async def get_login_page(request: Request):
    try:
        await get_current_user(
            get_token(request)
        )
        return RedirectResponse(url="/web/client", status_code=status.HTTP_302_FOUND)
    except Exception as ex:
        print("Пользователь не авторизован: exception: {}".format(ex))

    return templates.TemplateResponse(
        request=request,
        name='logon.html'
    )


@router.get("/client", response_class=HTMLResponse, summary="Информационный дашбоард")
async def get_client_page(request: Request):
    try:
        await get_current_user(
            get_token(request)
        )
    except Exception as ex:
        print("Пользователь не авторизован: exception: {}".format(ex))
        return RedirectResponse(url="/web", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='client.html'
    )
