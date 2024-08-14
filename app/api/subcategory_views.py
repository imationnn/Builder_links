from fastapi import APIRouter, Depends, Query
from starlette import status

from app.repository.redis_storage import TYPE_CHAPTER
from app.services.category_service import CategoryService
from app.schemas.api_schemas import Subcategory


subcategory_router = APIRouter(prefix="/subcategory", tags=["Subcategory"])


@subcategory_router.post(
    "/add",
    summary="Добавить subcategories",
    status_code=status.HTTP_201_CREATED,
    description="Subcategory должны быть вида: cat=131044 или subject=6546"
)
async def add_subcategories(
        subcategories: Subcategory,
        category_service: CategoryService = Depends(CategoryService)
) -> None:
    return await category_service.add_subcategories(subcategories)


@subcategory_router.delete(
    "/delete",
    summary="Удалить subcategories",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_subcategories(
        category_name: str,
        type_chapter: TYPE_CHAPTER,
        subcategories: list[str] = Query(description="должны быть вида: cat=131044 или subject=6546"),
        category_service: CategoryService = Depends(CategoryService)
) -> None:
    return await category_service.delete_subcategories(
        category_name,
        type_chapter,
        subcategories
    )
