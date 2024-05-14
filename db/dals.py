import uuid
from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import PortalRole, Point, TypePay, User, Position, Visit


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
            .where(and_(User.user_id == user_id, User.is_active == True))
            .values(kwargs)
            .returning(User.user_id)
        )
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]

    async def restore_user(self, user_id: UUID) -> Union[UUID, None]:
        query = (
            update(User)
            .where(User.user_id == user_id)
            .values(is_active=True)
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
    ) -> Position:
        new_position = Position(
            name=name,
        )
        self.db_session.add(new_position)
        await self.db_session.flush()
        return new_position

    async def delete_position(self, id: UUID) -> Union[UUID, None]:
        query = (
            update(Position)
            .where(and_(Position.id == id, Position.is_active == True))
            .values(is_active=False)
            .returning(Position.id)
        )
        res = await self.db_session.execute(query)
        deleted_position_id_row = res.fetchone()
        if deleted_position_id_row is not None:
            return deleted_position_id_row[0]


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
