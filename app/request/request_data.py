import asyncio

from httpx_client import HTTPXClient, DataResponse
from app.schemas.schemas_dto import SubCategoryDTO
from app.create_links import create_filter_url


URL_MAIN_MENU = "https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json"


class RequestData(HTTPXClient):

    async def get_main_menu(self) -> list[dict]:
        response = await self.get(URL_MAIN_MENU, timeout=5)
        if not response.data:
            pass  # TODO добавить оповещение
        await self.close_client()
        return response.data

    async def get_xsubjects(
            self,
            sub_cat: list[SubCategoryDTO],
            chunk_size: int = 30,
            time_sleep_between_request: int | float = 0.1,
            time_sleep_between_chunk: int | float = 1
    ) -> list[DataResponse]:
        offset = 0
        result: list[DataResponse] = []
        while offset < len(sub_cat):
            tasks = []
            for item in sub_cat[offset:offset + chunk_size]:
                url = create_filter_url(item.shard, item.query)
                task = asyncio.create_task(self.get(url, item))
                tasks.append(task)
                await asyncio.sleep(time_sleep_between_request)
            result.extend(await asyncio.gather(*tasks))
            offset += chunk_size
            await asyncio.sleep(time_sleep_between_chunk)
        await self.close_client()
        return result
