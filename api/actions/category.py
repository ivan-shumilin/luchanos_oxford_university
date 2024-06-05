from typing import Union

from sqlalchemy import select

from api.schemas import CategoryCreate, CategoryShow
from db.dals import CategoryDAL
from db.models import Category, Position


async def _get_category_by_name(category_name, session) -> Union[Category, None]:
    async with session.begin():
        category_dal = CategoryDAL(session)
        category = await category_dal.get_category_by_name(
            category_name=category_name,
        )
        if category is not None:
            return category


async def _get_category_by_id(category_id, session) -> Union[Category, None]:
    async with session.begin():
        category_dal = CategoryDAL(session)
        category = await category_dal.get_category_by_id(
            category_id=category_id,
        )
        if category is not None:
            return category


async def get_position_by_category(category_id: int, db):
    query = select(Position).where(Position.category_id == category_id)
    result = await db.execute(query)
    return result.scalars().all()


async def _create_new_category(body: CategoryCreate, session) -> CategoryShow:
    async with session.begin():
        category_dal = CategoryDAL(session)
        category = await category_dal.create_category(
            name=body.name,
        )
        return CategoryShow(
            id=category.id,
            name=category.name,
            is_active=category.is_active,
        )


async def _update_category(
        updated_category_params: dict, category_id: int, session
) -> Union[int, None]:
    async with session.begin():
        point_dal = CategoryDAL(session)
        updated_category_id = await point_dal.update_category(
            category_id=category_id, **updated_category_params,
        )
        return updated_category_id


async def _delete_category(category_id: int, session) -> Union[int, None]:
    async with session.begin():
        category_dal = CategoryDAL(session)
        deleted_category_id = await category_dal.delete_category(
            category_id=category_id,
        )
        positions_on_category = await get_position_by_category(category_id, session)
        for position in positions_on_category:
            position.is_active = False
        await session.commit()
        return deleted_category_id

