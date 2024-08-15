import asyncio
import itertools

from app.repository.redis_storage import RedisStorage
from app.schemas.schemas_dto import SubCategoryDTO, CategoryDTO
from app.repository.redis_storage import TYPE_CHAPTER


class Compare:
    def __init__(self, repository: RedisStorage):
        self.repository = repository

    async def compare_subcategory(
            self,
            category_name: str,
            old_good_subcategory: set[str],
            old_bad_subcategory: set[str],
            new_good_subcategory: set[str],
            new_bad_subcategory: set[str],
            new_subcategory: list[SubCategoryDTO],
            filtered_subcategories: list[SubCategoryDTO]
    ) -> list[SubCategoryDTO]:
        if ((len(old_good_subcategory) == len(new_good_subcategory)
                and len(old_bad_subcategory) == len(new_bad_subcategory))
                and not new_subcategory):
            return filtered_subcategories
        old_good_subcategory.difference_update(new_good_subcategory)
        old_bad_subcategory.difference_update(new_bad_subcategory)

        good_subcategory = await self._get_and_delete_subcategories(category_name, old_good_subcategory, "good")
        bad_subcategory = await self._get_and_delete_subcategories(category_name, old_bad_subcategory, "bad")

        if new_subcategory:
            await self.repository.add_subcategory_to_catalog(category_name, new_subcategory)
            filtered_subcategories = await self._process_new_subcategories(
                new_subcategory,
                good_subcategory,
                bad_subcategory,
                filtered_subcategories,
                category_name
            )
        return filtered_subcategories

    async def _get_and_delete_subcategories(
            self,
            category_name: str,
            subcategories: set[str],
            subcategory_type: TYPE_CHAPTER
    ):
        if not subcategories:
            return []
        fetched_subcategories = await asyncio.gather(
            *[self.repository.get_and_del_subcategory_from_catalog(category_name, i) for i in subcategories]
        )
        await self.repository.delete_subcategory(category_name, subcategory_type, *subcategories)
        return fetched_subcategories

    async def _process_new_subcategories(
            self,
            new_subcategory: list[SubCategoryDTO],
            good_subcategory: list[list[str, str]],
            bad_subcategory: list[list[str, str]],
            filtered_subcategories: list[SubCategoryDTO],
            category_name: str
    ) -> list[SubCategoryDTO]:

        good_subcategory = itertools.chain.from_iterable(good_subcategory)
        bad_subcategory = itertools.chain.from_iterable(bad_subcategory)
        last_new_subcategory = []

        for subcat in new_subcategory:
            if subcat.name in good_subcategory or subcat.url in good_subcategory:
                await self.repository.add_subcategory(category_name, "good", subcat.query)
                filtered_subcategories.append(subcat)
            elif subcat.name in bad_subcategory or subcat.url in bad_subcategory:
                await self.repository.add_subcategory(category_name, "bad", subcat.query)
            else:
                last_new_subcategory.append(subcat)

        if last_new_subcategory:
            await self.repository.add_category_for_notification(CategoryDTO(category_name, last_new_subcategory))
        return filtered_subcategories
