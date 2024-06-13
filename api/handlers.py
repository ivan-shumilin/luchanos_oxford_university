from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.actions.category import _get_category_by_name, _update_category, _create_new_category, _get_category_by_id, \
    _delete_category
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
    TypePayShow, VisitCreate, VisitShow, DeletePointResponse, ShowUser, CategoryCreate, ShowCategory, \
    DeleteCategoryResponse
from api.schemas import ShowUser
from api.schemas import UpdatedUserResponse
from api.schemas import UpdateUserRequest
from api.schemas import UserCreate
from db.models import User, Position, PortalRole
from db.session import get_db
from api.actions.scripts import send_messang, restore_db
from hashing import Hasher


user_router = APIRouter()


@user_router.post("/")
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> Union[UUID, None, ShowUser]:
    user = await _get_user_by_tg(body.tg_username, db)

    # случай когда создают пользователя, который ранее был создан и впоследствии удален
    if user:
        logger.info(f'Восстанволение пользователя {user.name} {user.surname} {user.point} -> {body.name} {body.surname} {body.point}')
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
        logger.error(f"Почта {user.email} пользвователя {body.name} {body.surname} уже используется")
        raise HTTPException(
            status_code=404,
            detail={"name": f"Почта {body.email} уже используется."}
        )
    user = await _get_user_by_phone(body.phone, db)
    if user is not None:
        logger.error(f"Телефон {user.phone} пользвователя {body.name} {body.surname} уже используется")
        raise HTTPException(
            status_code=404,
            detail={"name": f"Телефон {body.phone} уже используется."}
        )
    try:
        logger.info(f"Создание нового пользователя {body.name} {body.surname} {body.point}")
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
        logger.error(f"Пользователь {body.name} {body.surname} не найден.")
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
        logger.error(f"Пользователь {user_id} не найден.")
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if not check_user_permissions(
            target_user=user_for_deletion,
            current_user=current_user,
    ):
        logger.error(f"Недостаточно прав для удаления пользователя")
        raise HTTPException(status_code=403, detail="Forbidden.")
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        logger.error(f"Пользователь с id {user_id} не найден")
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
    logger.info("Предоставление прав администратора")
    if not current_user.is_superadmin:
        logger.error(f"{current_user.name} не имеет достаточно прав")
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.user_id == user_id:
        logger.error(f"{current_user.name} пытался предоставить права самому себе")
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_promotion = await _get_user_by_id(user_id, db)
    if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
        logger.error(f"{current_user.name} уже является администратором")
        raise HTTPException(
            status_code=409,
            detail=f"User with id {user_id} already promoted to admin / superadmin.",
        )
    if user_for_promotion is None:
        logger.error(f"Пользователь с id {user_id} не найден")
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
    logger.info("Удаление прав администратора")
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


@user_router.patch("/change_password")
async def change_user_password(user_id: UUID, new_password: str,
                               db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user_from_token)):
    logger.info(f"Смена пароля для пользователя {user_id}")
    if PortalRole.ROLE_PORTAL_SUPERADMIN not in current_user.roles:
        logger.error(f"Пользователь {current_user.name} {current_user.surname} не является администратором")
        raise HTTPException(
            status_code=403,
            detail={"name": f"У пользователя {current_user.name} недостаточно прав"}
        )

    target_user = _get_user_by_id(user_id, db)
    if not target_user:
        logger.error(f"Пользователь {user_id} не найден")
        raise HTTPException(
            status_code=404,
            detail={"name": f"Пользователь {user_id} не найден"}
        )

    try:
        query = update(User).where(User.user_id == user_id).values(
            hashed_password=Hasher.get_password_hash(new_password))
        await db.execute(query)
        await db.commit()

        return {
            "status": 200,
            "detail": {"name": f"Пароль обновлен"}
        }
    except Exception as e:
        logger.error(f"Ошибка сервера {e}")
        raise HTTPException(
            status_code=500,
            detail={"name": f"Ошибка сервера {e}"}
        )


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
) -> ShowUser:
    try:
        user = await _get_user_by_id(user_id, db)
    except:
        logger.error("Ошибка сервера")
        await send_messang("Ошибка сервера")
        date = await restore_db()
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if user is None:
        logger.info(f"Пользователь {user_id} не найден")
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
    logger.info(f"Начало обновление пользователя по id {user_id}")
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        logger.error("Обновление не может быть пустым")
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user_for_update = await _get_user_by_id(user_id, db)
    if user_for_update is None:
        logger.info(f"Пользователь {user_id} не найден")
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    if user_id != current_user.user_id:
        if check_user_permissions(
                target_user=user_for_update, current_user=current_user
        ):
            logger.error(f"Пользователь {current_user.name} {current_user.surname} не является администратором")
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
                "category_id": body.category_id,
                "is_active": True
            }
            await _update_position(data, position.id, db)
            return ShowPosition(
                id=position.id,
                name=body.name,
                category_id=body.category_id,
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
        logger.error(f"Должность с id {position_id} не найдена")
        raise HTTPException(
            status_code=404, detail=f"Point with id {position_for_deletion} not found."
        )

    deleted_point_id = await _delete_position(position_id, db)
    if deleted_point_id is None:
        logger.error(f"Должность с id {position_id} не получилось удалить")
        raise HTTPException(
            status_code=404, detail=f"Cant delete point with id {position_id}."
        )
    return DeletePointResponse(deleted_point_id=deleted_point_id)


@user_router.get("/positions")
async def get_positions(db: AsyncSession = Depends(get_db)):
    logger.info("Получение всех позиций")
    positions = await db.execute(select(Position))
    positions = positions.scalars().all()
    return positions


@user_router.put("/position")
async def update_position(position_id: int,
                          body: PositionCreate,
                          db: AsyncSession = Depends(get_db),
                          ) -> Union[UUID, None]:
    logger.info("Обновление должности {position_id}")
    position = await _get_position_by_id(position_id, db)

    if position is None:
        logger.error(f"Должность {body.name} не найдена.")
        raise HTTPException(
            status_code=404,
            detail={"name": f"Должность {body.name} не найдена."}
        )

    try:
        data = {
            "name": body.name,
            "category_id": body.category_id
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
        logger.info(f"Восстановление точки {body.name}")
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
    logger.info(f"Удаление заведения {point_id}")
    point_for_deletion = await _get_point_by_id(point_id, db)

    if point_for_deletion is None:
        logger.error(f"Заведение с id {point_id} не найдено")
        raise HTTPException(
            status_code=404, detail=f"Point with id {point_id} not found."
        )

    deleted_point_id = await _delete_point(point_id, db)
    if deleted_point_id is None:
        logger.error(f"Заведение с id {point_id} не получилось удалить")
        raise HTTPException(
            status_code=404, detail=f"Cant delete point with id {point_id}."
        )
    return DeletePointResponse(deleted_point_id=deleted_point_id)


@user_router.put("/point")
async def update_point(point_id: int,
                       body: PointCreate,
                       db: AsyncSession = Depends(get_db),
                       ) -> Union[UUID, None]:
    logger.info(f"Обновление заведения {point_id}")
    point = await _get_point_by_id(point_id, db)

    if point is None:
        logger.error(f"Заведение с id {point_id} не найдена")
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


@user_router.post("/category")
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Создание категории {body.name}")
    category = await _get_category_by_name(body.name, db)

    if category:
        try:
            data = {
                "name": body.name,
                "is_active": True
            }
            await _update_category(data, category.id, db)
            return ShowCategory(
                id=category.id,
                name=category.name
            )
        except IntegrityError as err:
            logger.error(err)
            raise HTTPException(status_code=503, detail=f"Database error: {err}")
    try:
        return await _create_new_category(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.put("/category")
async def update_category(category_id: int,
                          body: CategoryCreate,
                          db: AsyncSession = Depends(get_db),
                          ) -> Union[int, None]:
    logger.info(f"Обновление категории с id {category_id}")
    category = await _get_category_by_id(category_id, db)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail={"name": f"Категория {body.name} не найдена."}
        )

    try:
        data = {
            "name": body.name,
        }
        return await _update_category(data, category_id, db)

    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(
            status_code=503,
            detail={"name": f"Database error: {err}"}
        )


@user_router.delete("/category")
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_db),
) -> DeleteCategoryResponse:
    logger.info(f"Удаление категории {category_id}")
    category_for_deletion = await _get_category_by_id(category_id, db)

    if category_for_deletion is None:
        logger.error(f"Категория {category_id} не найдена")
        raise HTTPException(
            status_code=404, detail=f"Category with id {category_id} not found."
        )

    deleted_category_id = await _delete_category(category_id, db)
    if deleted_category_id is None:
        logger.error(f"Не получилось удалить категорию {category_id}")
        raise HTTPException(
            status_code=404, detail=f"Cant delete point with id {category_id}."
        )
    return DeleteCategoryResponse(deleted_category_id=deleted_category_id)
