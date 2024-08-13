from pydantic import BaseModel

from app.repository.redis_storage import TYPE_CHAPTER


class Subcategory(BaseModel):
    category_name: str
    list_subcategory: list[str]
    type_chapter: TYPE_CHAPTER


class Xsubject(BaseModel):
    category_name: str
    list_xsubjects: list[str | int]
    type_chapter: TYPE_CHAPTER


class RegisterParserIn(BaseModel):
    categories: list[str]
    path: str


class RegisterParserOut(BaseModel):
    category_name: str
    urls: set
