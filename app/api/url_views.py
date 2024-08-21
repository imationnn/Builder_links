from starlette import status
from fastapi import APIRouter, Depends, Query, BackgroundTasks

from app.services.service_utils import check_category_exist
from app.client import Builder


url_router = APIRouter(prefix="/url", tags=["Urls"])


@url_router.put(
    "/create",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Создать ссылки по категориям",
    description="Запускает процесс создания ссылок по переданным категориям"
)
async def create_url(
        background_tasks: BackgroundTasks,
        category_names: list[str] = Query(),
        builder: Builder = Depends(),
) -> None:
    categories = [check_category_exist(category_name) for category_name in category_names]
    background_tasks.add_task(builder.build, categories=categories, first_request=True)
