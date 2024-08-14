import logging
from typing import Any

from retryhttp import retry
from httpx import AsyncClient, TransportError, HTTPStatusError, Response
from json import JSONDecodeError

from app.request.headers import headers
from app.schemas.schemas_dto import SubCategoryDTO

logger = logging.getLogger(__name__)


class ExceptionForRetry(HTTPStatusError):
    def __init__(self):
        self.response = Response(status_code=500)


class DataResponse:
    def __init__(self, response: list | dict = None, args: SubCategoryDTO | None = None):
        self.data = response or {}
        self.args = args


class HTTPXClient:
    def __init__(self):
        self._client: AsyncClient | None = None
        self.response = DataResponse

    def _create_client(self) -> AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = AsyncClient()
        return self._client

    async def close_client(self):
        await self._client.aclose()

    @retry(server_error_codes=(429, 500, 502, 503, 504))
    async def _get(self, client: AsyncClient, url: str, timeout: int | float) -> Any:
        try:
            response = await client.get(url, headers=headers, timeout=timeout)
            return response.raise_for_status().json()
        except (TransportError, JSONDecodeError):
            raise ExceptionForRetry

    async def get(self, url: str, args: Any = None, timeout: int | float = 2) -> DataResponse:
        client = self._create_client()
        data = None
        try:
            data = await self._get(client, url, timeout)
        except Exception as e:
            logger.error("%s, %s", e, url)
        return self.response(data, args)
