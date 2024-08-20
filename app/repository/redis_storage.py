from typing import Literal
import pickle

from fastapi import Depends
from redis.asyncio import Redis

from app.config.settings import RedisConfig
from app.schemas.schemas_dto import SubCategoryDTO, XsubjectDTO, CategoryDTO, NotifyItem
from app.utils import (get_translate_category_name,
                       category_name_to_name_without_underscore,
                       get_lst_category_name_without_underscore)


SUBCATEGORY = "subcat"
XSUBJECTS = "xsubjects"
CATALOG = "catalog"
URLS = "urls"
REGISTRATION = "registration_of_parsers"
CAT_NOTIFY = "category_notification"
ITEMS_ALERTS = "items_sent_alerts"
SET_ITEMS_ALERTS = "set_items_sent_alerts"


TYPE_CHAPTER = Literal["good", "bad"]


class KeyBuilder:
    def __init__(self, separator: str = "_"):
        self.separator = separator

    def build(self, category: str, *args: str) -> str:
        category = get_translate_category_name(category)
        return self.separator.join([category, *args])


class RedisClient:
    def __init__(self):
        self.config = RedisConfig()
        self._redis = Redis(host=self.config.redis_host,
                            port=self.config.redis_port,
                            db=self.config.redis_db_name,
                            password=self.config.redis_password,
                            decode_responses=True)

    @property
    def redis(self) -> Redis:
        return self._redis

    async def client(self) -> Redis:
        async with self._redis as client:
            yield client

    async def close(self) -> None:
        await self._redis.aclose()


class RedisStorage:
    def __init__(self, redis_client: Redis = Depends(RedisClient().client)):
        self._redis = redis_client
        self.key_builder = KeyBuilder()

    async def add_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *subcat_items: str | int
    ) -> None:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        await self._redis.sadd(db_key, *subcat_items)

    async def add_xsubjects(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *xsubject_items: str | int
    ) -> None:
        db_key = self.key_builder.build(category_name, XSUBJECTS, chapter_type)
        await self._redis.sadd(db_key, *xsubject_items)

    async def get_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER
    ) -> set[str]:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        return await self._redis.smembers(db_key)

    async def get_xsubject(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER
    ) -> set[int]:
        db_key = self.key_builder.build(category_name, XSUBJECTS, chapter_type)
        return {int(xsubject) for xsubject in await self._redis.smembers(db_key)}

    async def delete_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *subcat_items: str | int
    ) -> None:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        await self._redis.srem(db_key, *subcat_items)

    async def delete_xsubject(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *xsubject_item: str | int
    ) -> None:
        db_key = self.key_builder.build(category_name, XSUBJECTS, chapter_type)
        await self._redis.srem(db_key, *xsubject_item)

    async def add_subcategory_to_catalog(
            self,
            category_name: str,
            lst_subcategory: list[SubCategoryDTO]
    ) -> None:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, CATALOG)
        data = {i.query: f"{i.name}|{i.url}" for i in lst_subcategory}
        await self._redis.hset(db_key, mapping=data)

    async def get_and_del_subcategory_from_catalog(
            self,
            category_name: str,
            subcategory: str
    ) -> list[str, str] | list:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, CATALOG)
        value = await self._redis.hget(db_key, subcategory)
        if value:
            value = value.split("|")
            await self._redis.hdel(db_key, subcategory)
        return value or ["", ""]

    async def check_subcategory_catalog(self, category_name: str) -> bool:
        return bool(await self._redis.exists(self.key_builder.build(category_name, SUBCATEGORY, CATALOG)))

    async def add_xsubjects_to_catalog(
            self,
            category_name: str,
            lst_xsubjects: list[XsubjectDTO]
    ) -> None:
        db_key = self.key_builder.build(category_name, XSUBJECTS, CATALOG)
        data = {i.id: i.name for i in lst_xsubjects}
        await self._redis.hset(db_key, mapping=data)

    async def get_and_del_xsubject_from_catalog(
            self,
            category_name: str,
            xsubject: str | int
    ) -> str:
        db_key = self.key_builder.build(category_name, XSUBJECTS, CATALOG)
        xsubject = str(xsubject)
        value = await self._redis.hget(db_key, xsubject)
        if value:
            await self._redis.hdel(db_key, xsubject)
        return value or ""

    async def add_urls(self, category_name: str, *urls: str) -> None:
        db_key = self.key_builder.build(category_name, URLS)
        await self._redis.sadd(db_key, *urls)

    async def get_urls(self, category_name: str) -> set:
        db_key = self.key_builder.build(category_name_to_name_without_underscore(category_name), URLS)
        return await self._redis.smembers(db_key)

    async def delete_urls(self, category_name: str) -> None:
        db_key = self.key_builder.build(category_name, URLS)
        await self._redis.delete(db_key)

    async def add_parser_to_register(self, category: str | list[str], url: str) -> None:
        if isinstance(category, str):
            category = [category]
        data = {i: url for i in get_lst_category_name_without_underscore(category)}
        await self._redis.hset(REGISTRATION, mapping=data)

    async def get_parser_url(self, category_name: str) -> str:
        return await self._redis.hget(REGISTRATION, category_name)

    async def delete_parser_from_register(self, category: str | list[str]) -> None:
        if isinstance(category, str):
            category = [category]
        await self._redis.hdel(REGISTRATION, *get_lst_category_name_without_underscore(category))

    async def get_categories_for_parsing(self) -> list[str] | list:
        return await self._redis.hkeys(REGISTRATION)

    async def add_category_for_notification(self, category: CategoryDTO) -> None:
        await self._redis.sadd(CAT_NOTIFY, pickle.dumps(category).decode('latin1'))

    async def get_category_for_notification(self) -> list[CategoryDTO] | list:
        return [pickle.loads(category.encode('latin1')) for category in await self._redis.smembers(CAT_NOTIFY)]

    async def delete_category_for_notification(self) -> None:
        await self._redis.delete(CAT_NOTIFY)

    async def check_exists_item_for_notification(self, item: str | int) -> bool:
        return bool(await self._redis.sismember(SET_ITEMS_ALERTS, item))

    async def add_items_for_sent_alerts(
            self,
            data: dict[int, NotifyItem],
            notify_items: list[str | int]
    ) -> None:
        data = {k: pickle.dumps(v).decode('latin1') for k, v in data.items()}
        await self._redis.hset(ITEMS_ALERTS, mapping=data)
        await self._redis.sadd(SET_ITEMS_ALERTS, *notify_items)

    async def get_item_from_db_sent_alerts(self, item_id: str | int) -> NotifyItem | None:
        item: str | None = await self._redis.hget(ITEMS_ALERTS, item_id)
        if item:
            item: NotifyItem = pickle.loads(item.encode('latin1'))
            await self._redis.srem(SET_ITEMS_ALERTS, item.subcategory or item.xsubject)
            await self._redis.hdel(ITEMS_ALERTS, item_id)
        return item

    async def get_all_items_waiting_to_be_added(self) -> dict[int, NotifyItem] | dict:
        return {int(k): pickle.loads(v.encode('latin1')) for k, v in (await self._redis.hgetall(ITEMS_ALERTS)).items()}

    async def get_last_item_alert_key(self) -> int:
        return max(map(int, await self._redis.hkeys(ITEMS_ALERTS)), default=0)
