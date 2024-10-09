import datetime
from typing import Union

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from loguru import logger
from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from api.actions.category import _get_category_by_id
from api.actions.point import _get_point_by_id
from api.actions.position import _get_position_by_id
from api.actions.user import _get_user_by_id
from db.models import User, Position, Point, TypePay, Visit, Category, PortalRole
from db.session import get_db
import pandas as pd

from reports.helpers import get_formatted_year_and_month, rounding_down, rounding_up
from managment.commands import upload_to_ydisk
from reports.report import create_report, collecting_data

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


@router.get("/")
def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/recover-password")
def recover_password(request: Request):
    return templates.TemplateResponse("auth/recover-password.html", {"request": request})


@router.get("/forgot-password")
def forgot_password(request: Request):
    return templates.TemplateResponse("auth/forgot-password.html", {"request": request})


@router.get("/job-title")
async def get_position(request: Request, db: AsyncSession = Depends(get_db)):
    position_id = int(request.query_params.get('position_id', None))
    position = await _get_position_by_id(position_id, db)
    token: str = request.query_params.get('token', None)
    user_id = request.query_params.get('user_id', None)

    categories = await db.scalars(select(Category).where(Category.is_active == True))
    categories = categories.all()

    print(categories)

    if token and user_id:
        return templates.TemplateResponse(
            "job-title.html",
            {
                "categories": categories,
                "user_id": user_id,
                "token": token,
                "request": request,
                "position": position,
            }
        )

    return RedirectResponse(url='/login')


@router.get("/job-title-add")
async def job_title_add(request: Request, token: str, user_id: str, db: AsyncSession = Depends(get_db)):
    categories = await db.execute(select(Category).where(Category.is_active == True))
    categories = categories.scalars().all()

    return templates.TemplateResponse(
        "job-title-add.html",
        {
            "categories": categories,
            "request": request,
            "token": token,
            "user_id": user_id,
            "page": "job_title",
        }
    )


@router.get("/job-title-list")
async def job_title_list(request: Request, token: str, user_id: str, db: AsyncSession = Depends(get_db),
                         ):
    positions = await db.execute(
        select(Position).where(Position.is_active == True).options(joinedload(Position.category)))
    positions = positions.scalars().all()

    for position in positions:
        try:
            users = await db.execute(select(User).where(and_(User.position == position.id, User.is_active == True)))
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
async def admin(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    employees = await db.execute(select(User).where(User.is_active == True))
    employees_count = len(employees.scalars().all())

    points = await db.execute(select(Point).where(Point.is_active == True))
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

    positions = await db.execute(select(Position).where(Position.is_active == True))
    positions = positions.scalars().all()

    points = await db.execute(select(Point).where(Point.is_active == True))
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
async def get_employee(request: Request, db: AsyncSession = Depends(get_db)):
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
            "employee.html",
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

    points = await db.execute(select(Point).where(Point.is_active == True))
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


@router.get("/point")
async def get_point(request: Request, db: AsyncSession = Depends(get_db)):
    point_id = int(request.query_params.get('point_id', None))
    token: str = request.query_params.get('token', None)
    user_id = request.query_params.get('user_id', None)

    point = await _get_point_by_id(point_id, db)

    if token and user_id:
        return templates.TemplateResponse(
            "point.html",
            {
                "user_id": user_id,
                "token": token,
                "request": request,
                "point": point,
            }
        )

    return RedirectResponse(url='/login')


@router.get("/categories-list")
async def categories_list(request: Request, db: AsyncSession = Depends(get_db)):
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    query = (
        select(Category.name, Category.id,
               func.count(func.distinct(case([(Position.is_active == True, Position.name)])))).
        select_from(Category).
        outerjoin(Position, Category.id == Position.category_id).
        where(Category.is_active == True).
        group_by(Category.name, Category.id)
    )

    categories = await db.execute(query)
    categories = categories.all()

    if token and user_id:
        return templates.TemplateResponse(
            "categories-list.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
                "categories": categories,
            }
        )
    return RedirectResponse(url='/login')


@router.get("/category-add")
def category_add(request: Request):

    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    if token and user_id:
        return templates.TemplateResponse(
            "category-add.html",
            {
                "request": request,
                "token": token,
                "user_id": user_id,
            }
        )
    return RedirectResponse(url='/login')


@router.get("/category")
async def get_category(request: Request, db: AsyncSession = Depends(get_db)):

    category_id = int(request.query_params.get('category_id', None))
    token: str = request.query_params.get('token', None)
    user_id = request.query_params.get('user_id', None)

    category = await _get_category_by_id(category_id, db)

    if token and user_id:
        return templates.TemplateResponse(
            "category.html",
            {
                "user_id": user_id,
                "token": token,
                "request": request,
                "category": category,
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

    query = (
        select(
            Visit.created_at,
            User.name + ' ' + User.surname,
            Point.name,
        ).select_from(Visit)
        .join(User, Visit.user_id == User.user_id)
        .join(Point, User.point == Point.id)
        .where(and_(
            User.is_active == True,
            Point.is_active == True,
            Visit.is_active == True,
            )
        )
    )
    visits = await db.execute(query)
    visits = visits.all()

    # Преобразование данных в DataFrame
    df = pd.DataFrame([(str(v[0].date()), v[1], v[2], v[0]) for v in visits],
                      columns=['date', 'user', 'point', 'time'])

    # Группировка по дате и пользователю
    grouped = df.groupby(['date', 'user'])

    # Получение самых ранних и поздних времен для каждой группы
    result = grouped.agg({'time': ['min', 'max'], 'point': 'first'})

    DELTA_MOSCOW_TIME = datetime.timedelta(hours=3)

    # Преобразование результата в список словарей
    output = []
    for (date, user), row in result.iterrows():
        min_time = rounding_down((row[('time', 'min')] + DELTA_MOSCOW_TIME))
        max_time = rounding_up((row[('time', 'max')] + DELTA_MOSCOW_TIME))
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


@router.get('/report_info')
async def get_report_info(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Создание отчета посещаемости")
    token: str = request.query_params.get('token', None)
    user_id: str = request.query_params.get('user_id', None)

    user = await _get_user_by_id(user_id, db)
    is_admin = PortalRole.ROLE_PORTAL_SUPERADMIN in user.roles or PortalRole.ROLE_PORTAL_ADMIN in user.roles

    if token and user_id and is_admin:
        month, year = get_formatted_year_and_month()
        # month, year = '10', 2023
        data, hours_data = await collecting_data(month, year, db)
        try:
            create_report(month, year, data, hours_data, db)
        except Exception as e:
            response = e
            logger.error(e)
            print(e)
        try:
            loadfile = f'static/reports/report_{month}_{year}.xlsx'  # локальный путь
            savefile = f'report_time_tracking/report_{month}_{year}.xlsx'  # путь на диске
            response = await upload_to_ydisk(loadfile, savefile)
        except Exception as e:
            response = e
            logger.error(e)
            print(e)
        return templates.TemplateResponse(
            "report_info.html",
            {
                "user_id": user_id,
                "token": token,
                "request": request,
                "response": response,
            }
        )

    return RedirectResponse(url='/login')

