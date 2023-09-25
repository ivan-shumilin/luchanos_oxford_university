from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from db.models import User
from db.session import get_db

router = APIRouter(
    prefix="",
    tags=["Pages"],
)

templates = Jinja2Templates(directory="templates")
@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("auth/base.html", {"request": request})

@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/recover-password")
def recover_password(request: Request):
    return templates.TemplateResponse("auth/recover-password.html", {"request": request})

@router.get("/forgot-password")
def forgot_password(request: Request):
    return templates.TemplateResponse("auth/forgot-password.html", {"request": request})

@router.get("/job_title")
def job_title(request: Request, token: str, user_id: str):
    return templates.TemplateResponse(
        "job_title.html",
        {
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "job_title",
        }
    )

@router.get("/")
def admin(request: Request, token: str, user_id: str):
    # здесь можно использовать значение параметра token для авторизации запросов
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "admin",
        }
    )


# @router.get("/{token}")
# async def admin(
#         request: Request,
#         current_user: User = Depends(get_current_user_from_token)
# ):
#     return templates.TemplateResponse(
#         "admin.html",
#         {
#             "request": request,
#             "token": token,
#         }
#     )
