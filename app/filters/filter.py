from copy import deepcopy

from app.repository.redis_storage import RedisStorage
from app.schemas.schemas_dto import CategoryDTO, SubCategoryDTO, XsubjectDTO
from app.filters.compare import Compare


class CategoryFilter:
    def __init__(self, repository: RedisStorage):
        self.repository = repository
        self.compare = Compare(self.repository)

    async def filter_subcategory(self, lst_categories: list[CategoryDTO]) -> list[CategoryDTO]:
        for category in lst_categories:
            old_good_subcategory = await self.repository.get_subcategory(category.category, "good")
            old_bad_subcategory = await self.repository.get_subcategory(category.category, "bad")

            if not old_good_subcategory and not old_bad_subcategory:
                continue

            new_good_subcategory = set()
            new_bad_subcategory = set()
            new_subcategory = []
            filtered_subcategory = []

            for subcat in category.sub_cat_dto:  # type: SubCategoryDTO
                if subcat.query in old_good_subcategory:
                    filtered_subcategory.append(subcat)
                    new_good_subcategory.add(subcat.query)
                elif subcat.query in old_bad_subcategory:
                    new_bad_subcategory.add(subcat.query)
                else:
                    if not await self.repository.check_exists_item_for_notification(subcat.query):
                        new_subcategory.append(subcat)

            category.sub_cat_dto = await self.compare.compare_subcategory(
                category.category,
                old_good_subcategory,
                old_bad_subcategory,
                new_good_subcategory,
                new_bad_subcategory,
                new_subcategory,
                filtered_subcategory
            )
        return lst_categories

    async def _filter_xsubjects(
            self,
            subcat: SubCategoryDTO,
            good_xsubjects: set[int],
            bad_xsubjects: set[int]
    ) -> tuple[list[XsubjectDTO], list[XsubjectDTO]]:

        filtered_xsubjects = []
        new_xsubjects = []

        for xsubject in subcat.xsubjects:
            if xsubject.id in good_xsubjects:
                filtered_xsubjects.append(xsubject)
            elif xsubject.id not in bad_xsubjects and not await self.repository.check_exists_item_for_notification(
                    xsubject.id
            ):
                new_xsubjects.append(xsubject)

        return filtered_xsubjects, new_xsubjects

    async def filter_xsubjects(
            self,
            lst_categories: list[CategoryDTO],
    ) -> list[CategoryDTO]:
        for category in lst_categories:
            good_xsubjects: set = await self.repository.get_xsubject(category.category, "good")
            bad_xsubjects: set = await self.repository.get_xsubject(category.category, "bad")

            if not good_xsubjects and not bad_xsubjects:
                continue

            new_subcats = []
            filtered_subcategory = []

            for subcat in category.sub_cat_dto:  # type: SubCategoryDTO
                filtered_xsubjects, new_xsubjects = await self._filter_xsubjects(
                    subcat,
                    good_xsubjects,
                    bad_xsubjects
                )
                if filtered_xsubjects or not subcat.xsubjects:
                    subcat.xsubjects = filtered_xsubjects
                    filtered_subcategory.append(subcat)

                if new_xsubjects:
                    new_subcat = deepcopy(subcat)
                    new_subcat.xsubjects = new_xsubjects
                    new_subcats.append(new_subcat)

            if new_subcats:
                await self.repository.add_category_for_notification(CategoryDTO(category.category, new_subcats))
            category.sub_cat_dto = filtered_subcategory
        return lst_categories
