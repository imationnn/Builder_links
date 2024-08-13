from fastapi import HTTPException
from starlette import status

from app.config.categories import MAIN_CATEGORIES
from app.utils import category_name_to_name_without_underscore


def check_category_exist(category_name: str) -> str:
    category_name = category_name_to_name_without_underscore(category_name)
    if category_name not in MAIN_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_name} does not exist"
        )
    return category_name
