import uuid
from datetime import date
from typing import Union
from uuid import UUID

from sqlalchemy import and_, extract
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import PortalRole, Point, TypePay, User, Position, Visit, Category


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class UserDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self,
        name: str,
        surname: str,
        patronymic: str,
        tg_username: str,
        email: str,
        phone: str,
        hashed_password: str,
        roles: list[PortalRole],
        position: int,
        point: int,
        type_pay: int,
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            patronymic=patronymic,
            tg_username=tg_username,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            roles=roles,
            position=position,
            point=point,
            type_pay=type_pay,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_tg(self, tg_username: str) -> Union[User, None]:
        query = select(User).where(User.tg_username == tg_username)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_phone(self, phone: str) -> Union[User, None]:
        query = select(User).where(User.phone == phone)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]

    async def restore_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(kwargs, is_active=True)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]


class PositionDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_position(
        self,
        name: str,
        category_id: int
    ) -> Position:
        new_position = Position(
            name=name,
            category_id=category_id
        )
        self.db_session.add(new_position)
        await self.db_session.flush()
        return new_position

    async def delete_position(self, position_id: int) -> Union[int, None]:
        query = (
            update(Position)
            .where(and_(Position.id == position_id, Position.is_active == True))
            .values(is_active=False)
            .returning(Position.id)
        )
        res = await self.db_session.execute(query)
        deleted_position_id_row = res.fetchone()
        if deleted_position_id_row is not None:
            return deleted_position_id_row[0]

    async def get_position_by_id(self, position_id: int) -> Union[Position, None]:
        query = select(Position).where(Position.id == position_id)
        result = await self.db_session.scalar(query)
        return result

    async def get_position_by_name(self, position_name: str) -> Union[Point, None]:
        query = select(Position).where(Position.name == position_name)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def update_position(self, position_id: int, **kwargs) -> Union[int, None]:
        query = (
            update(Position)
            .where(Position.id == position_id)
            .values(kwargs)
            .returning(Position.id)
        )
        res = await self.db_session.execute(query)
        update_position_id_row = res.fetchone()
        if update_position_id_row is not None:
            return update_position_id_row[0]


class PointDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_point(
        self,
        name: str,
        address: str,
        coordinates: str,
    ) -> Point:
        new_point = Point(
            name=name,
            address=address,
            coordinates=coordinates,
        )
        self.db_session.add(new_point)
        await self.db_session.flush()
        return new_point

    async def get_point_by_id(self, point_id: int) -> Union[Point, None]:
        query = select(Point).where(Point.id == point_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_point_by_address(self, point_address: str) -> Union[Point, None]:
        query = select(Point).where(Point.address == point_address)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def delete_point(self, point_id: int) -> Union[int, None]:
        query = (
            update(Point)
            .where(and_(Point.id == point_id, Point.is_active == True))
            .values(is_active=False)
            .returning(Point.id)
        )
        res = await self.db_session.execute(query)
        deleted_point_id_row = res.fetchone()
        if deleted_point_id_row is not None:
            return deleted_point_id_row[0]

    async def update_point(self, point_id: int, **kwargs) -> Union[int, None]:
        query = (
            update(Point)
            .where(Point.id == point_id)
            .values(kwargs)
            .returning(Point.id)
        )
        res = await self.db_session.execute(query)
        update_point_id_row = res.fetchone()
        if update_point_id_row is not None:
            return update_point_id_row[0]


class CategoryDAL:
    """Data Access Layer for operating category info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_category(
        self,
        name: str,
    ) -> Category:
        new_category = Category(
            name=name,
        )
        self.db_session.add(new_category)
        await self.db_session.flush()
        return new_category

    async def delete_category(self, category_id: int) -> Union[int, None]:
        query = (
            update(Category)
            .where(and_(Category.id == category_id, Category.is_active == True))
            .values(is_active=False)
            .returning(Category.id)
        )
        res = await self.db_session.execute(query)
        deleted_category_id_row = res.fetchone()
        if deleted_category_id_row is not None:
            return deleted_category_id_row[0]

    async def update_category(self, category_id: int, **kwargs) -> Union[int, None]:
        query = (
            update(Category)
            .where(Category.id == category_id)
            .values(kwargs)
            .returning(Category.id)
        )
        res = await self.db_session.execute(query)
        update_category_id_row = res.fetchone()
        if update_category_id_row is not None:
            return update_category_id_row[0]

    async def get_category_by_name(self, category_name: str) -> Union[Category, None]:
        query = select(Category).where(Category.name == category_name)
        res = await self.db_session.scalar(query)
        if res is not None:
            return res

    async def get_category_by_id(self, category_id: int) -> Union[Category, None]:
        query = select(Category).where(Category.id == category_id)
        res = await self.db_session.scalar(query)
        if res is not None:
            return res


class TypePayDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_type_pay(
        self,
        name: str,
    ) -> TypePay:
        new_type_pay = TypePay(
            name=name,
        )
        self.db_session.add(new_type_pay)
        await self.db_session.flush()
        return new_type_pay


class VisitDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_visit(
        self,
        user_id: uuid.UUID,
        point: int,
    ) -> Visit:
        new_visit = Visit(
            user_id=user_id,
            point=point,
        )
        self.db_session.add(new_visit)
        await self.db_session.flush()
        return new_visit

    async def check_visit(self, user_id: uuid.UUID) -> bool:
        current_time = date.today()
        query = select(Visit).where(and_(Visit.user_id == user_id,
                                         extract('month', Visit.created_at) == current_time.month,
                                         extract('year', Visit.created_at) == current_time.year,
                                         extract('day', Visit.created_at) == current_time.day)
                                    )
        return await self.db_session.scalar(query)
