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
        xsubject_id: str | int | None = None
) -> str:
    url = CATALOG_URL.format(shard, query, sort=sort)
    if xsubject_id is not None:
        url = url + f"&xsubject={xsubject_id}"
    return url


class ConstructUrl:
    def __init__(self, repository: RedisStorage):
        self.repository = repository

    @staticmethod
    def _select_type_sorting(
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
        if min_count < count < max_count:
            sorts = PRICE_UP, PRICE_DOWN
        else:
            sorts = POPULAR,
        return [create_catalog_url(shard, query, sort, xsubject_id) for sort in sorts]

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
