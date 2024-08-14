from fastapi import APIRouter, Depends, Query
from starlette import status

from app.repository.redis_storage import TYPE_CHAPTER
from app.services.category_service import CategoryService
from app.schemas.api_schemas import Xsubject


xsubject_router = APIRouter(prefix="/xsubject", tags=["Xsubjects"])


@xsubject_router.post(
    "/add",
    summary="Добавить xsubject",
    status_code=status.HTTP_201_CREATED,
    description="Xsubjects должны быть просто числами"
)
async def add_xsubjects(
        xsubjects: Xsubject,
        category_service: CategoryService = Depends(CategoryService)
) -> None:
    return await category_service.add_xsubjects(xsubjects)


@xsubject_router.delete(
    "/delete",
    summary="Удалить xsubject",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_xsubjects(
        category_name: str,
        type_chapter: TYPE_CHAPTER,
        xsubjects: list[str | int] = Query(description="должны быть просто числами"),
        category_service: CategoryService = Depends(CategoryService)
) -> None:
    return await category_service.delete_xsubjects(
        category_name,
        type_chapter,
        xsubjects
    )
