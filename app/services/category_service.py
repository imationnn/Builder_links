from fastapi import Depends

from app.repository.redis_storage import RedisStorage, TYPE_CHAPTER
from app.schemas.api_schemas import Subcategory, Xsubject
from app.services.service_utils import check_category_exist


class CategoryService:
    def __init__(self, repository: RedisStorage = Depends()):
        self.repository = repository

    async def add_subcategories(self, subcategory: Subcategory) -> None:
        category_name = check_category_exist(subcategory.category_name)
        await self.repository.add_subcategory(
            category_name,
            subcategory.type_chapter,
            *subcategory.list_subcategory
        )

    async def delete_subcategories(
            self,
            category_name: str,
            type_chapter: TYPE_CHAPTER,
            subcategories: list[str]
    ) -> None:
        category_name = check_category_exist(category_name)
        await self.repository.delete_subcategory(
            category_name,
            type_chapter,
            *subcategories
        )

    async def add_xsubjects(self, xsubject: Xsubject) -> None:
        category_name = check_category_exist(xsubject.category_name)
        await self.repository.add_xsubjects(
            category_name,
            xsubject.type_chapter,
            *xsubject.list_xsubjects
        )

    async def delete_xsubjects(
            self,
            category_name: str,
            type_chapter: TYPE_CHAPTER,
            xsubjects: list[str]
    ) -> None:
        category_name = check_category_exist(category_name)
        await self.repository.delete_xsubject(
            category_name,
            type_chapter,
            *xsubjects
        )
