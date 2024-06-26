from typing import Union
from uuid import UUID

from fastapi import HTTPException
from loguru import logger

from api.schemas import ShowUser
from api.schemas import UserCreate
from db.dals import UserDAL
from db.models import PortalRole
from db.models import User
from hashing import Hasher


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    logger.info(f"Создание нового пользователя {body.name} {body.surname} {body.point} {body.tg_username}")
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            patronymic=body.patronymic,
            tg_username=body.tg_username,
            email=body.email,
            phone=body.phone,
            hashed_password=Hasher.get_password_hash(body.password),
            roles=[
                PortalRole.ROLE_PORTAL_USER,
            ],
            position=body.position,
            point=body.point,
            type_pay=body.type_pay,
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            patronymic=user.patronymic,
            tg_username=user.tg_username,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            position=user.position,
            point=user.point,
            type_pay=user.type_pay,
        )


async def _delete_user(user_id, session) -> Union[UUID, None]:
    logger.info(f"Удаление пользователя {user_id}")
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(
            user_id=user_id,
        )
        return deleted_user_id


async def _update_user(
    updated_user_params: dict, user_id: UUID, session
) -> Union[UUID, None]:
    logger.info(f"Обновление пользователя {user_id}: {updated_user_params}")
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params,
        )
        return updated_user_id


async def _get_user_by_id(user_id, session) -> Union[User, None]:
    logger.info(f"Получение пользователя {user_id} по id")
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


async def _get_user_by_email(email, session) -> Union[User, None]:
    logger.info(f"Получение пользователя {email} по email")
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_email(
            email=email,
        )
        if user is not None:
            return user


async def _get_user_by_tg(tg_username, session) -> Union[User, None]:
    logger.info(f"Получение пользователя {tg_username} по никнейму телеграмма")
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_tg(
            tg_username=tg_username,
        )
        if user is not None:
            return user


async def _get_user_by_phone(phone, session) -> Union[User, None]:
    logger.info(f"Получение пользователя {phone} по номеру телефона")
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_phone(
            phone=phone,
        )
        if user is not None:
            return user


def check_user_permissions(target_user: User, current_user: User) -> bool:
    logger.info(f"Проверка пользовательских ({target_user.name} {target_user.surname}) расрешений")
    if PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id != current_user.user_id:
        # check admin role
        if not {
            PortalRole.ROLE_PORTAL_ADMIN,
            PortalRole.ROLE_PORTAL_SUPERADMIN,
        }.intersection(current_user.roles):
            return False
        # check admin deactivate superadmin attempt
        if (
            PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
        # check admin deactivate admin attempt
        if (
            PortalRole.ROLE_PORTAL_ADMIN in target_user.roles
            and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False
    return True
