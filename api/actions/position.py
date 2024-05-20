from typing import Union

from sqlalchemy import select

from api.schemas import ShowPosition, PositionCreate
from db.dals import PositionDAL
from db.models import Position, User


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


async def _get_position_by_id(position_id: int, session) -> Union[Position, None]:
    async with session.begin():
        position_dal = PositionDAL(session)
        position = await position_dal.get_position_by_id(position_id=position_id)
        return position


async def get_users_by_position(position_id: int, db):
    query = select(User).where(User.position == position_id)
    result = await db.scalars(query)
    return result.all()


async def _delete_position(position_id, session) -> Union[int, None]:
    async with session.begin():
        position_dal = PositionDAL(session)
        deleted_position_id = await position_dal.delete_position(
            position_id=position_id,
        )
        users_on_position = await get_users_by_position(position_id, session)
        for user in users_on_position:
            user.is_active = False
        await session.commit()
        return deleted_position_id


async def _update_position(
        updated_point_params: dict, position_id: int, session
) -> Union[int, None]:
    async with session.begin():
        point_dal = PositionDAL(session)
        updated_point_id = await point_dal.update_position(
            position_id=position_id, **updated_point_params,
        )
        return updated_point_id


async def _get_position_by_name(position_name, session) -> Union[Position, None]:
    async with session.begin():
        position_dal = PositionDAL(session)
        position = await position_dal.get_position_by_name(
            position_name=position_name,
        )
        if position is not None:
            return position
