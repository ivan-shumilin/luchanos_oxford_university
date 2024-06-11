import time

from loguru import logger

from api.schemas import VisitCreate, VisitShow
from db.dals import VisitDAL


async def _create_new_visit(body: VisitCreate, session) -> VisitShow:
    logger.info(f"Создание нового посещения: {body.point} {time.time()} {body.user_id}")
    if not session.is_active:
        async with session.begin():
            visit_dal = VisitDAL(session)
            visit = await visit_dal.create_visit(
                user_id=body.user_id,
                point=body.point,
            )
            return VisitShow(
                id=visit.id,
                user_id=visit.user_id,
                point=visit.point,
                is_active=visit.is_active,
                created_at=visit.created_at,
            )
    else:
        visit_dal = VisitDAL(session)
        visit = await visit_dal.create_visit(
            user_id=body.user_id,
            point=body.point,
        )
        return VisitShow(
            id=visit.id,
            user_id=visit.user_id,
            point=visit.point,
            is_active=visit.is_active,
            created_at=visit.created_at,
        )