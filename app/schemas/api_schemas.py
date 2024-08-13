from pydantic import BaseModel

from app.repository.redis_storage import TYPE_CHAPTER


class Subcategory(BaseModel):
    category_name: str
    list_subcategory: list[str]
    type_chapter: TYPE_CHAPTER
