import datetime
from typing import Union

from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.templating import _TemplateResponse

from api.actions.auth import get_current_user_from_token
from api.actions.user import _get_user_by_id
from db.models import User, Position, Point, TypePay, Visit
from db.session import get_db
import pandas as pd

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
async def job_title_list(request: Request, token: str, user_id: str, db: AsyncSession = Depends(get_db)):

    positions = await db.execute(select(Position))
    positions = positions.scalars().all()

    for position in positions:
        try:
            users = await db.execute(select(User).where(User.position == position.id))
            users_count = len(users.scalars().all())
        except:
            users_count = 0
        position.users_count = users_count

    return templates.TemplateResponse(
        "job-title-list.html",
        {
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "job_title",
            "positions": positions,
        }
    )

@router.get("/admin")
async def admin(request: Request,  db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    employees = await db.execute(select(User))
    employees_count = len(employees.scalars().all())

    points = await db.execute(select(Point))
    points_count = len(points.scalars().all())

    if token and user_id:
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "admin",
                "employees_count": employees_count,
                "points_count": points_count,
            }
        )
    return RedirectResponse(url='/login')


@router.get("/employees-list")
async def employees_list(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    employees = await db.execute(select(User).where(User.is_active == True))
    employees = employees.scalars().all()

    for employee in employees:
        try:
            point = await db.execute(select(Point).where(Point.id == employee.point))
            point = point.scalar()
            point_name = f'{point.name}'
        except:
            point_name = employee.point
        employee.point_name = point_name

        try:
            position = await db.execute(select(Position).where(Position.id == employee.position))
            position = position.scalar()
            position_name = f'{position.name}'
        except:
            position_name = employee.position
        employee.position_name = position_name

        try:
            type_pay = await db.execute(select(TypePay).where(TypePay.id == employee.type_pay))
            type_pay = type_pay.scalar()
            type_pay_name = f'{type_pay.name}'
        except:
            type_pay_name = employee.type_pay
        employee.type_pay_name = type_pay_name


    if token and user_id:
        return templates.TemplateResponse(
            "employees-list.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "employees",
                "employees": employees,
            }
        )
    return RedirectResponse(url='/login')


@router.get("/employees-add")
async def employees_add(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    positions = await db.execute(select(Position))
    positions = positions.scalars().all()

    points = await db.execute(select(Point))
    points = points.scalars().all()

    type_pays = await db.execute(select(TypePay))
    type_pays = type_pays.scalars().all()

    if token and user_id:
        return templates.TemplateResponse(
            "employees-add.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "employees",
                "positions": positions,
                "points": points,
                "type_pays": type_pays,
            }
        )
    return RedirectResponse(url='/login')


@router.get("/employee")
async def get_employee(request: Request, db: AsyncSession = Depends(get_db)) -> \
        Union[_TemplateResponse, RedirectResponse]:
    employee_id = request.query_params.get('employee_id', None)
    employee = await _get_user_by_id(employee_id, db)
    token: str = request.query_params.get('token', None)
    user_id = request.query_params.get('user_id', None)

    if employee is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {employee_id} not found."
        )

    if token and user_id:

        positions = await db.execute(select(Position))
        positions = positions.scalars().all()

        points = await db.execute(select(Point))
        points = points.scalars().all()

        type_pays = await db.execute(select(TypePay))
        type_pays = type_pays.scalars().all()

        return templates.TemplateResponse(
            "user.html",
            {
                "user_id": user_id,
                "token": token,
                "request": request,
                "employee": employee,
                "positions": positions,
                "points": points,
                "type_pays": type_pays,
            }
        )

    return RedirectResponse(url='/login')


@router.get("/points-list")
async def points_list(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    points = await db.execute(select(Point))
    points = points.scalars().all()

    for p in points:
        try:
            users = await db.execute(select(User).where(User.point == p.id))
            users_count = len(users.scalars().all())
        except:
            users_count = 0
        p.users_count = users_count

    if token and user_id:
        return templates.TemplateResponse(
            "points-list.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "points",
                "points": points,
            }
        )
    return RedirectResponse(url='/login')

@router.get("/points-add")
def points_add(request: Request):
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
async def visits_journal(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    visits = await db.execute(select(Visit))
    visits = visits.scalars().all()


    for v in visits:
        try:
            user = await db.execute(select(User).where(User.user_id == v.user_id))
            user = user.scalar()
            full_name = f'{user.name} {user.surname}'
        except:
            full_name = v.user_id
        v.full_name = full_name

        try:
            point = await db.execute(select(Point).where(Point.id == v.point))
            point = point.scalar()
            point = f'{point.name}'
        except:
            point = v.point
        v.point_name = point

    # Преобразование данных в DataFrame
    df = pd.DataFrame([(str(v.created_at.date()), str(v.full_name), str(v.point_name), v.created_at) for v in visits],
                      columns=['date', 'user', 'point', 'time'])

    # Группировка по дате и пользователю
    grouped = df.groupby(['date', 'user'])

    # Получение самых ранних и поздних времен для каждой группы
    result = grouped.agg({'time': ['min', 'max'], 'point': 'first'})

    DELTA_MOSCOW_TIME = datetime.timedelta(hours=3)

    # Преобразование результата в список словарей
    output = []
    for (date, user), row in result.iterrows():
        min_time = (row[('time', 'min')] + DELTA_MOSCOW_TIME).hour + 1
        max_time = (row[('time', 'max')] + DELTA_MOSCOW_TIME).hour
        if min_time > max_time:
            max_time = min_time

        output.append({
            'date': date,
            'full_name': user,
            'point': str(row['point']['first']),
            'min_time': min_time,
            'max_time': max_time,
            'total_hours': max_time - min_time,
        })

    if token and user_id:
        return templates.TemplateResponse(
            "visits_journal.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "page": "visits_journal",
                "output": output,
            }
        )
    return RedirectResponse(url='/login')
