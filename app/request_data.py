import asyncio

from httpx_client import HTTPXClient, DataResponse
from app.schemas.schemas_dto import FilterUrlDTO


URL_MAIN_MENU = "https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json"


class RequestData:
    def __init__(self, client: HTTPXClient = HTTPXClient()):
        self._client = client

    async def get_main_menu(self) -> list[dict]:
        response = await self._client.get(URL_MAIN_MENU)
        if not response.data:
            pass  # TODO добавить оповещение
        await self._client.close_client()
        return response.data

    async def get_xsubjects(
            self,
            filter_urls: list[FilterUrlDTO],
            chunk_size: int = 30,
            time_sleep_between_request: int = 0.1,
            time_sleep_between_chunk: int = 1
    ) -> list[DataResponse]:
        offset = 0
        result: list[DataResponse] = []
        while offset < len(filter_urls):
            tasks = []
            for item in filter_urls[offset:offset + chunk_size]:
                task = asyncio.create_task(self._client.get(item.filter_url, item.category_dto))
                tasks.append(task)
                await asyncio.sleep(time_sleep_between_request)
            result.extend(await asyncio.gather(*tasks))
            offset += chunk_size
            await asyncio.sleep(time_sleep_between_chunk)
        await self._client.close_client()
        return result
