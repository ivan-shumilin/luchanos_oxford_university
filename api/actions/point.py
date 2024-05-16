from typing import Union

from sqlalchemy import select

from api.schemas import PointCreate, ShowPoint, TypePayCreate, TypePayShow, VisitCreate, VisitShow
from db.dals import PointDAL, TypePayDAL
from db.models import Point, User


async def _create_new_point(body: PointCreate, session) -> ShowPoint:
    async with session.begin():
        point_dal = PointDAL(session)
        point = await point_dal.create_point(
            name=body.name,
            address=body.address,
            coordinates=body.coordinates,
        )
        return ShowPoint(
            id=point.id,
            name=point.name,
            address=point.address,
            coordinates=point.coordinates,
            is_active=point.is_active,
        )


async def _get_point_by_id(point_id, session) -> Union[Point, None]:
    async with session.begin():
        point_dal = PointDAL(session)
        point = await point_dal.get_point_by_id(
            point_id=point_id,
        )
        if point is not None:
            return point


async def get_users_by_point(point_id: int, db):
    query = select(User).where(User.point == point_id)
    result = await db.execute(query)
    return result.scalars().all()


async def _delete_point(point_id, session) -> Union[int, None]:
    async with session.begin():
        point_dal = PointDAL(session)
        deleted_point_id = await point_dal.delete_point(
            point_id=point_id,
        )
        users_on_point = await get_users_by_point(point_id, session)
        for user in users_on_point:
            user.is_active = False
        await session.commit()
        return deleted_point_id


async def _update_point(
    updated_point_params: dict, point_id: int, session
) -> Union[int, None]:
    async with session.begin():
        point_dal = PointDAL(session)
        updated_point_id = await point_dal.update_point(
            point_id=point_id, **updated_point_params,
        )
        return updated_point_id


async def _create_new_type_pay(body: TypePayCreate, session) -> TypePayShow:
    async with session.begin():
        type_pay_dal = TypePayDAL(session)
        type_pay = await type_pay_dal.create_type_pay(
            name=body.name,
        )
        return TypePayShow(
            id=type_pay.id,
            name=type_pay.name,
            is_active=type_pay.is_active,
        )
