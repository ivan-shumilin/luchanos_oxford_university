from api.schemas import PointCreate, ShowPoint, TypePayCreate, TypePayShow, VisitCreate, VisitShow
from db.dals import PointDAL, TypePayDAL


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
