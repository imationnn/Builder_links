from fastapi import APIRouter

from app.api.subcategory_views import subcategory_router
from app.api.xsubject_views import xsubject_router
from app.api.url_views import url_router
from app.api.register_parser_views import register_router


main_router = APIRouter()
main_router.include_router(subcategory_router)
main_router.include_router(xsubject_router)
main_router.include_router(url_router)
main_router.include_router(register_router)
