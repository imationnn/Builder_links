from typing import Sequence, Literal

from redis.asyncio import Redis

from app.config.settings import RedisConfig
from app.schemas.schemas_dto import SubCategoryDTO
from app.utils import get_translate_category_name


SUBCATEGORY = "subcat"
XSUBJECTS = "xsubjects"
CATALOG = "catalog"

TYPE_CHAPTER = Literal["good", "bad", "neutral"]


class KeyBuilder:
    def __init__(self, separator: str = "_"):
        self.separator = separator

    def build(self, category: str, *args: Sequence[str]) -> str:
        category = get_translate_category_name(category)
        return self.separator.join([category, *args])


class RedisStorage:
    def __init__(self, redis_config: RedisConfig = RedisConfig(), key_builder=KeyBuilder()):
        self.config = redis_config
        self.key_builder = key_builder
        self._redis = Redis(host=self.config.redis_host,
                            port=self.config.redis_port,
                            db=self.config.redis_db_name,
                            password=self.config.redis_password,
                            decode_responses=True)

    async def add_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *subcat_items: str | int | Sequence[str | int]
    ) -> None:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        await self._redis.sadd(db_key, *subcat_items)

    async def add_xsubjects(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *xsubject_items: str | int | Sequence[str | int]
    ) -> None:
        db_key = self.key_builder.build(category_name, XSUBJECTS, chapter_type)
        await self._redis.sadd(db_key, *xsubject_items)

    async def check_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            subcat_item: str
    ) -> bool:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        return bool(await self._redis.sismember(db_key, subcat_item))

    async def check_xsubject(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            xsubject_item: str
    ) -> bool:
        db_key = self.key_builder.build(category_name, XSUBJECTS, chapter_type)
        return bool(await self._redis.sismember(db_key, xsubject_item))

    async def delete_subcategory(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *subcat_items: str | int | Sequence[str | int]
    ) -> None:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, chapter_type)
        await self._redis.srem(db_key, *subcat_items)

    async def delete_bad_xsubject(
            self,
            category_name: str,
            chapter_type: TYPE_CHAPTER,
            *xsubject_item: str | int | Sequence[str | int]
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

    async def get_subcategory_from_catalog(
            self,
            category_name: str,
            subcategory: str
    ) -> list[str, str] | list:
        db_key = self.key_builder.build(category_name, SUBCATEGORY, CATALOG)
        value = await self._redis.hget(db_key, subcategory)
        if value:
            value = value.split("|")
            await self._redis.hdel(db_key, subcategory)
        return value or []

    async def close(self) -> None:
        await self._redis.aclose()
