from fastapi import APIRouter, Depends, Query
from starlette import status

from app.services.registration_parser_service import RegistrationService
from app.schemas.api_schemas import RegisterParserIn, RegisterParserOut


register_router = APIRouter(prefix="/register", tags=["Register parser"])


@register_router.post(
    "/add",
    summary="Зарегистрировать парсер",
    status_code=status.HTTP_200_OK,
    description="Добавляет регистрацию парсера. Необходимо передать одну или несколько категорий списком и "
                "путь в парсере по которому он принимает ссылки для работы."
)
async def add_registration_parser(
        registration: RegisterParserIn,
        registration_service: RegistrationService = Depends(RegistrationService)
) -> list[RegisterParserOut]:
    return await registration_service.add_registration(registration)


@register_router.delete(
    "/delete",
    summary="Удалить регистрацию парсера",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаляет регистрацию парсера. Необходимо передать одну или несколько категорий."
)
async def delete_registration_parser(
        category_name: list[str] = Query(),
        registration_service: RegistrationService = Depends(RegistrationService)
) -> None:
    return await registration_service.delete_registration(category_name)
