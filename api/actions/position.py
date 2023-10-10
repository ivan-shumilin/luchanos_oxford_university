from api.schemas import ShowPosition, PositionCreate
from db.dals import PositionDAL


async def _create_new_position(body: PositionCreate, session) -> ShowPosition:
    async with session.begin():
        position_dal = PositionDAL(session)
        position = await position_dal.create_position(
            name=body.name,
        )
        return ShowPosition(
            id=position.id,
            name=position.name,
            is_active=position.is_active,
        )
