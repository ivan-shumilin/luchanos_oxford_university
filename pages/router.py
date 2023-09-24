from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


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

@router.get("/")
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
