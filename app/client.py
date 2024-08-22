from fastapi import Depends
import logging

from app import parser
from app.filters.filter import CategoryFilter
from app.notification import Notification
from app.repository.redis_storage import RedisStorage
from app.request.request_data import RequestData
from app.create_links import ConstructUrl
from app.schemas.schemas_dto import CategoryDTO


logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, repository: RedisStorage = Depends()):
        self.repository = repository
        self.request = RequestData()
        self.notify = Notification(repository)
        self.filter = CategoryFilter(repository)
        self.url_constructor = ConstructUrl(repository)

    async def get_main_menu(self) -> list[dict]:
        main_menu = await self.request.get_main_menu()
        if not main_menu:
            msg = "Could not get main menu, check the link."
            logger.error(msg)
            await self.notify.send_notification(msg)
        return main_menu

    async def add_subcategory_to_catalog(self, categories: list[CategoryDTO]) -> None:
        for category in categories:
            if not await self.repository.check_subcategory_catalog(category.category):
                await self.repository.add_subcategory_to_catalog(category.category, category.sub_cat_dto)

    async def request_and_add_xsubjects_to_subcategory(self, categories: list[CategoryDTO]) -> list[CategoryDTO]:
        for category in categories:
            logger.info("Getting xsubjects to category %s", category.category)
            category.sub_cat_dto = parser.get_xsubjects_from_response(
                await self.request.get_xsubjects(category.sub_cat_dto)
            )
        return categories

    async def build(self, categories: list[str], first_request: bool = False) -> None:
        logger.info("Starts getting data for categories %s", str(categories).strip("[]"))
        main_menu = await self.get_main_menu()
        if not main_menu:
            return
        parse_categories = parser.get_all_data_from_main_menu_by_desired_categories(main_menu, categories)
        if first_request:
            await self.add_subcategory_to_catalog(parse_categories)
        filtered_categories = await self.filter.filter_subcategory(parse_categories)
        categories_with_xsubjects = await self.request_and_add_xsubjects_to_subcategory(filtered_categories)
        filtered_categories = await self.filter.filter_xsubjects(categories_with_xsubjects)
        await self.url_constructor.create_and_save_catalog_urls(filtered_categories)
        await self.notify.start_notify()
        logger.info("Finished getting data for categories %s", str(categories).strip("[]"))

    async def send_urls_to_registered_parsers(self) -> None:
        urls_parser = await self.repository.get_parser_urls()
        for category_name, url in urls_parser.items():
            urls = await self.repository.get_urls(category_name)
            await self.request.post(url, json={"category_name": category_name, "urls": [*urls]})
