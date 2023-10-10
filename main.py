import json

import sentry_sdk
import uvicorn
import aiohttp
from fastapi import FastAPI, Request, Depends
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware

import settings
from api.actions.visit import _create_new_visit
from api.handlers import user_router
from api.login_handler import login_router
from api.schemas import VisitCreate
from api.service import service_router
from db.models import User
from db.models import Point as Points
from db.session import get_db
from pages.router import router as router_pages
from schemas import Answer

from geopy.distance import distance
from geopy.point import Point

from swh import TG_API

# sentry configuration
sentry_sdk.init(
    dsn=settings.SENTRY_URL,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
app = FastAPI(title="luchanos-oxford-university")

# origins = [
#     "http://localhost:3000",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
#     allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
#                    "Authorization"],
# )

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
main_api_router.include_router(service_router, tags=["service"])
app.include_router(main_api_router)


###########################
# BLOCK WITH PAGES ROUTES #
###########################
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router_pages)


################
# TG BOT #######
################
LOCATIONS = [
    {
        'name': 'Алкон',
        'location': {
            'latitude': 55.805278,
            'longitude': 37.520588,
        }
    },
    {
        'name': 'Сколково',
        'location': {
            'latitude': 55.685162,
            'longitude': 37.350982,
        }
    }
]

def get_point(latitude: float, longitude: float) -> Point:
    return Point(latitude=latitude, longitude=longitude)

@app.post("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await request.json()
    obj = Answer.parse_obj(result)
    print(obj)

    reply_markup = {
        "keyboard":
            [
                [
                    {
                        "request_location": True,
                        "text": "Отправить локацию",
                    }
                ],
            ],
         "resize_keyboard": True,
         "one_time_keyboard": True,
    }

    # проверка, есть ли геоданные
    if obj.message.location == None:
        answer = 'Для отправки геоданных нажмите "Отправить локацию"'
    else:
        target_point = get_point(obj.message.location.latitude, obj.message.location.longitude)
        points = await db.execute(select(Points))
        points = points.scalars().all()
        point_id = None
        for point in points:
            latitude = point.coordinates.split(":")[0]
            longitude = point.coordinates.split(":")[1]
            dist = int(distance(
                    target_point,
                    get_point(latitude, longitude)
                ).m)
            if dist < 500:
                point_id = point.id
                point_name = point.name

        if not point_id:
            answer = f'Не находитесь на объекте'
        else:
            # проверяем есть ли пользователь в системе приславший локацию
            received_username = obj.message.from_tg.username

            try:
                user = await db.execute(select(User).where(User.tg_username == received_username))
                user = user.scalar()
            except:
                user = None
                answer = 'Вы не зарегистрированы в системе. Сообщите администратору.'

            if user:
                # записываем визит в базу
                body: VisitCreate = VisitCreate.parse_obj(
                    {
                        "user_id": "233f2c27-475a-40b1-986d-b823f7dd8a9f",
                        "point": point_id,
                    }
                )
                try:
                    res = await _create_new_visit(body, db)
                    print(res)
                    answer = f'Данные записаны. Местоположение: {point_name}'
                except:
                    answer = 'Ошибка сервера, повторите попытку'
            # except IntegrityError as err:
            #     logger.error(err)
    data = {
        'chat_id': obj.message.chat.id,
        'text': answer,
        'reply_markup': json.dumps(reply_markup)
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f'https://api.telegram.org/bot{TG_API}/sendMessage',
                data=data
        ) as response:
            print(response.status)

    return ({'status': 'OK'})


if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)