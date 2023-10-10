from api.schemas import ShowPosition, PositionCreate
from db.dals import TypePayDAL


async def _create_new_position(body: PositionCreate, session) -> ShowPosition:
    async with session.begin():
        type_pay_dal = TypePayDAL(session)
        type_pay = await type_pay_dal.create_type_pay(
            name=body.name,
        )
        return ShowPosition(
            id=type_pay.id,
            name=type_pay.name,
            is_active=type_pay.is_active,
        )
