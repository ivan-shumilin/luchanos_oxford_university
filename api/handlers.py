from logging import getLogger
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.actions.point import _create_new_point, _create_new_type_pay, _get_point_by_id, _delete_point, _update_point, \
    _get_point_by_address
from api.actions.position import _create_new_position, _get_position_by_id, _delete_position, _update_position, \
    _get_position_by_name
from api.actions.user import _create_new_user, _get_user_by_email, _get_user_by_phone, _get_user_by_tg
from api.actions.user import _delete_user
from api.actions.user import _get_user_by_id
from api.actions.user import _update_user
from api.actions.user import check_user_permissions
from api.actions.visit import _create_new_visit
from api.schemas import DeleteUserResponse, PositionCreate, ShowPosition, PointCreate, ShowPoint, TypePayCreate, \
    TypePayShow, VisitCreate, VisitShow, DeletePointResponse, ShowUser
from api.schemas import ShowUser
from api.schemas import UpdatedUserResponse
from api.schemas import UpdateUserRequest
from api.schemas import UserCreate
from db.models import User, Position
from db.session import get_db
from api.actions.scripts import send_messang, restore_db

logger = getLogger(__name__)

user_router = APIRouter()


@user_router.post("/")
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> Union[UUID, None, ShowUser]:
    user = await _get_user_by_tg(body.tg_username, db)

    # случай когда создают пользователя, который ранее был создан и впоследствии удален
    if user:
        try:
            data = {
                "name": body.name,
                "surname": body.surname,
                "patronymic": body.patronymic,
                "email": body.email,
                "phone": body.phone,
                "position": body.position,
                "point": body.point,
                "type_pay": body.type_pay,
                "is_active": True
            }
            await _update_user(data, user.user_id, db)
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

        except IntegrityError as err:
            logger.error(err)
            raise HTTPException(
                status_code=503,
                detail={"name": f"Database error: {err}"}
            )

    if user is not None:
        raise HTTPException(
            status_code=404,
            detail={"name": f"Почта {body.email} уже используется."}
        )
    user = await _get_user_by_phone(body.phone, db)
    if user is not None:
        raise HTTPException(
            status_code=404,
            detail={"name": f"Телефон {body.phone} уже используется."}
        )
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(
            status_code=503,
            detail={"name": f"Database error: {err}"}
        )


@user_router.put("/")
async def update_user(user_id: UUID,
                      body: UserCreate,
                      db: AsyncSession = Depends(get_db),
                      ) -> Union[UUID, None]:
    user = await _get_user_by_id(user_id, db)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь {body.name} {body.surname} не найден."
        )

    try:
        data = {
            "name": body.name,
            "surname": body.surname,
            "patronymic": body.patronymic,
            "tg_username": body.tg_username,
            "email": body.email,
            "phone": body.phone,
            "position": body.position,
            "point": body.point,
            "type_pay": body.type_pay
        }
        return await _update_user(data, user_id, db)

    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(
            status_code=503,
            detail={"name": f"Database error: {err}"}
        )


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> DeleteUserResponse:
    user_for_deletion = await _get_user_by_id(user_id, db)
    if user_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if not check_user_permissions(
            target_user=user_for_deletion,
            current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail="Forbidden.")
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/admin_privilege", response_model=UpdatedUserResponse)
async def grant_admin_privilege(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_promotion = await _get_user_by_id(user_id, db)
    if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user_id} already promoted to admin / superadmin.",
        )
    if user_for_promotion is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    updated_user_params = {
        "roles": user_for_promotion.enrich_admin_roles_by_admin_role()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, session=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.delete("/admin_privilege", response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_revoke_admin_privileges = await _get_user_by_id(user_id, db)
    if not user_for_revoke_admin_privileges.is_admin:
        raise HTTPException(
            status_code=409, detail=f"User with id {user_id} has no admin privileges."
        )
    if user_for_revoke_admin_privileges is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    updated_user_params = {
        "roles": user_for_revoke_admin_privileges.remove_admin_privileges_from_model()
    }
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, session=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
) -> ShowUser:
    error: bool = False
    try:
        user = await _get_user_by_id(user_id, db)
    except:
        await send_messang("Ошибка сервера")
        date = await restore_db()
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if user is None:
        await send_messang("Пользователь не найден")
        date = await restore_db()

        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )

    return user


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
        user_id: UUID,
        body: UpdateUserRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user_for_update = await _get_user_by_id(user_id, db)
    if user_for_update is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if user_id != current_user.user_id:
        if check_user_permissions(
                target_user=user_for_update, current_user=current_user
        ):
            raise HTTPException(status_code=403, detail="Forbidden.")
    try:
        updated_user_id = await _update_user(
            updated_user_params=updated_user_params, session=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.post("/position")
async def create_position(body: PositionCreate, db: AsyncSession = Depends(get_db)) -> ShowPosition:
    position = await _get_position_by_name(body.name, db)

    if position:
        try:
            data = {
                "name": body.name,
                "is_active": True
            }
            await _update_position(data, position.id, db)
            return ShowPosition(
                id=position.id,
                name=body.name,
                is_active=True
            )
        except IntegrityError as err:
            logger.error(err)
            raise HTTPException(status_code=503, detail=f"Database error: {err}")

    try:
        return await _create_new_position(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/position")
async def delete_position(
        position_id: int,
        db: AsyncSession = Depends(get_db),
) -> DeletePointResponse:
    position_for_deletion = await _get_position_by_id(position_id, db)

    if position_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"Point with id {position_for_deletion} not found."
        )

    deleted_point_id = await _delete_position(position_id, db)
    if deleted_point_id is None:
        raise HTTPException(
            status_code=404, detail=f"Cant delete point with id {position_id}."
        )
    return DeletePointResponse(deleted_point_id=deleted_point_id)


@user_router.get("/positions")
async def get_positions(db: AsyncSession = Depends(get_db)):
    positions = await db.execute(select(Position))
    positions = positions.scalars().all()
    return positions


@user_router.put("/position")
async def update_position(position_id: int,
                          body: PositionCreate,
                          db: AsyncSession = Depends(get_db),
                          ) -> Union[UUID, None]:
    position = await _get_position_by_id(position_id, db)

    if position is None:
        raise HTTPException(
            status_code=404,
            detail={"name": f"Должность {body.name} не найдена."}
        )

    try:
        data = {
            "name": body.name,
        }
        return await _update_position(data, position_id, db)

    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(
            status_code=503,
            detail={"name": f"Database error: {err}"}
        )


@user_router.post("/point")
async def create_point(body: PointCreate, db: AsyncSession = Depends(get_db)) -> ShowPoint:
    point = await _get_point_by_address(body.address, db)
    if point:
        try:
            data = {
                "name": body.name,
                "is_active": True
            }
            await _update_point(data, point.id, db)
            return ShowPoint(
                id=point.id,
                name=body.name,
                address=point.address,
                coordinates=point.coordinates,
                is_active=True,
            )
        except IntegrityError as err:
            logger.error(err)
            raise HTTPException(status_code=503, detail=f"Database error: {err}")
    try:
        return await _create_new_point(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/point")
async def delete_point(
        point_id: int,
        db: AsyncSession = Depends(get_db),
) -> DeletePointResponse:
    point_for_deletion = await _get_point_by_id(point_id, db)

    if point_for_deletion is None:
        raise HTTPException(
            status_code=404, detail=f"Point with id {point_id} not found."
        )

    deleted_point_id = await _delete_point(point_id, db)
    if deleted_point_id is None:
        raise HTTPException(
            status_code=404, detail=f"Cant delete point with id {point_id}."
        )
    return DeletePointResponse(deleted_point_id=deleted_point_id)


@user_router.put("/point")
async def update_point(point_id: int,
                       body: PointCreate,
                       db: AsyncSession = Depends(get_db),
                       ) -> Union[UUID, None]:
    point = await _get_point_by_id(point_id, db)

    if point is None:
        raise HTTPException(
            status_code=404,
            detail={"name": f"Заведение {body.name} не найден."}
        )

    try:
        data = {
            "name": body.name,
            "address": body.address,
            "coordinates": body.coordinates
        }
        return await _update_point(data, point_id, db)

    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(
            status_code=503,
            detail={"name": f"Database error: {err}"}
        )


@user_router.post("/type_pay")
async def create_type_pay(body: TypePayCreate, db: AsyncSession = Depends(get_db)) -> TypePayShow:
    try:
        return await _create_new_type_pay(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.post("/visit")
async def create_visit(body: VisitCreate, db: AsyncSession = Depends(get_db)) -> VisitShow:
    try:
        return await _create_new_visit(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
