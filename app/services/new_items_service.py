from fastapi import HTTPException, Depends

from app.repository.redis_storage import RedisStorage, TYPE_CHAPTER
from app.schemas.api_schemas import NewItemsOut


class NewItemService:
    def __init__(self, repository: RedisStorage = Depends()):
        self.repository = repository

    async def add_new_item_after_notification(self, db_id: str | int, type_chapter: TYPE_CHAPTER) -> None:
        item = await self.repository.get_item_from_db_sent_alerts(db_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Id {db_id} not found")
        if item.subcategory:
            await self.repository.add_subcategory(item.category_name, type_chapter, item.subcategory)
        elif item.xsubject:
            await self.repository.add_xsubjects(item.category_name, type_chapter, item.xsubject)

    async def get_all_new_items(self) -> list[NewItemsOut] | list:
        items = await self.repository.get_all_items_waiting_to_be_added()
        return [NewItemsOut(id=k, item=v) for k, v in sorted(items.items())]
