from fastapi import APIRouter, Depends, Query

from app.services.new_items_service import NewItemService
from app.schemas.api_schemas import NewItemsOut
from app.repository.redis_storage import TYPE_CHAPTER


new_items_router = APIRouter(prefix="/new-items", tags=["New Items"])


@new_items_router.get(
    "/all-new-items",
    summary="Получить все категории ожидающие добавления",
    description="Возвращает все категории ожидающие добавления, где id это номер записи в бд, а item сама запись"
)
async def get_all_new_items(
        new_item_service: NewItemService = Depends(NewItemService)
) -> list[NewItemsOut] | list:
    return await new_item_service.get_all_new_items()


@new_items_router.patch(
    "/add-new-item",
    summary="Добавить категорию ожидающую добавления",
    description="Добавляет категорию в бд из тех что ожидают добавления"
)
async def add_new_items(
        item_id: str | int = Query(description="id записи в бд, полученная через оповещение"),
        chapter_type: TYPE_CHAPTER = Query(description="тип бд в которую будет добавлена категория"),
        new_item_service: NewItemService = Depends(NewItemService)
) -> None:
    await new_item_service.add_new_item_after_notification(item_id, chapter_type)
