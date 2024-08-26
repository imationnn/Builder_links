from itertools import chain
from math import ceil

from app.schemas.schemas_dto import CategoryDTO
from app.config.settings import settings
from app.repository.redis_storage import RedisStorage


BASE_URL = "https://www.wildberries.ru{}"
FILTER_URL = "https://catalog.wb.ru/catalog/{}/v6/filters?ab_testing=false&appType=1&{}&curr=rub&dest=-1255987&spp=30"
CATALOG_URL = "https://catalog.wb.ru/catalog/{0}/v2/catalog?ab_testing=false&appType=1&{1}&curr=rub&dest=-1255987&page={{}}&sort={sort}&spp=30"

PRICE_UP = "priceup"
PRICE_DOWN = "pricedown"
POPULAR = "popular"


def create_site_url(path: str) -> str:
    return BASE_URL.format(path)


def create_filter_url(shard: str, query: str) -> str:
    return FILTER_URL.format(shard, query)


def create_catalog_url(
        shard: str,
        query: str,
        sort: str,
        count_page: int,
        xsubject_id: str | int | None = None
) -> list[str]:
    url = CATALOG_URL.format(shard, query, sort=sort)
    if xsubject_id is not None:
        url = f"{url}&xsubject={xsubject_id}"
    return [url.format(page) for page in range(1, count_page + 1)]


class ConstructUrl:
    def __init__(self, repository: RedisStorage):
        self.repository = repository

    @classmethod
    def _get_count_page(
            cls,
            total: int,
            min_count: int,
            max_count: int,
            min_count_filter: int
    ) -> int:
        if total > max_count:
            total = min_count
        count_page, rest_count = divmod(total, 100)
        if rest_count >= min_count_filter:
            count_page += 1
        return count_page

    def _select_type_sorting(
            self,
            shard: str,
            query: str,
            count: int,
            min_count: int,
            max_count: int,
            min_count_filter: int,
            xsubject_id: str | int | None = None
    ) -> list[str]:
        if count < min_count_filter:
            return []
        count_page = self._get_count_page(count, min_count, max_count, min_count_filter)
        if min_count < count < max_count:
            sorts = PRICE_UP, PRICE_DOWN
            count_page = ceil(count_page / 2)
        else:
            sorts = POPULAR,
        return chain.from_iterable(
            [create_catalog_url(shard, query, sort, count_page, xsubject_id) for sort in sorts]
        )

    async def create_and_save_catalog_urls(
            self,
            lst_categories: list[CategoryDTO],
            min_count_product: int = settings.min_count_for_sort,
            max_count_product: int = settings.max_count_for_sort,
            min_count_filter: int = settings.min_count_for_filter
    ) -> None:
        for category in lst_categories:
            urls = []
            for subcategory in category.sub_cat_dto:
                for xsubject in subcategory.xsubjects:
                    urls.extend(self._select_type_sorting(
                        subcategory.shard,
                        subcategory.query,
                        xsubject.count,
                        min_count_product,
                        max_count_product,
                        min_count_filter,
                        xsubject.id
                    ))
                if not subcategory.xsubjects:
                    urls.extend(self._select_type_sorting(
                        subcategory.shard,
                        subcategory.query,
                        subcategory.total,
                        min_count_product,
                        max_count_product,
                        min_count_filter
                    ))
            if urls:
                await self._save_urls(category.category, urls)

    async def _save_urls(self, category_name: str, urls: list[str]) -> None:
        await self.repository.delete_urls(category_name)
        await self.repository.add_urls(category_name, *urls)
