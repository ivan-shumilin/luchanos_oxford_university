from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

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

@router.get("/job-title-add")
def job_title_add(request: Request, token: str, user_id: str):
    return templates.TemplateResponse(
        "job-title-add.html",
        {
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "job_title",
        }
    )

@router.get("/job-title-list")
def job_title_list(request: Request, token: str, user_id: str):
    return templates.TemplateResponse(
        "job-title-list.html",
        {
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "job_title",
        }
    )

@router.get("/admin")
def admin(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "admin",
            }
        )
    return RedirectResponse(url='/login')


@router.get("/employees-list")
def employees_list(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "employees-list.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "employees",
            }
        )
    return RedirectResponse(url='/login')

@router.get("/employees-add")
def employees_add(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "employees-add.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "employees",
            }
        )
    return RedirectResponse(url='/login')

@router.get("/points-list")
def points_list(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "points-list.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "points",
            }
        )
    return RedirectResponse(url='/login')

@router.get("/points-add")
def pointsaddt(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "points-add.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "points",
            }
        )
    return RedirectResponse(url='/login')


@router.get("/user-documentation")
def user_documentation(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "user-documentation.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "user-documentation",
            }
        )
    return RedirectResponse(url='/login')


@router.get("/visits_journal")
def visits_journal(request: Request):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "visits_journal.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "visits_journal",
            }
        )
    return RedirectResponse(url='/login')





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
