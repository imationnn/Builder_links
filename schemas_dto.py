from dataclasses import dataclass


@dataclass
class QueryShardUrlDTO:
    __slots__ = ("query", "shard", "url")
    query: str
    shard: str
    url: str


@dataclass
class CategoryDTO:
    __slots__ = ("category", "qsu_dto")
    category: str
    qsu_dto: list[QueryShardUrlDTO]


@dataclass
class FilterUrlDTO:
    __slots__ = ("filter_url", "category_dto")
    filter_url: str
    category_dto: QueryShardUrlDTO
