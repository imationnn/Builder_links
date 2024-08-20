from fastapi import HTTPException, Depends
from starlette import status

from app.repository.redis_storage import RedisStorage
from app.schemas.api_schemas import RegisterParserIn, RegisterParserOut
from app.services.service_utils import check_category_exist


class RegistrationService:
    def __init__(self, repository: RedisStorage = Depends()):
        self.repository = repository

    def __raise_error(self, category: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Urls for category {category} not found, start process create urls for this category"
        )

    async def add_registration(self, registration: RegisterParserIn) -> list[RegisterParserOut]:
        categories = [check_category_exist(name) for name in registration.categories]
        result = [
            RegisterParserOut(
                category_name=category,
                urls=urls
            ) if (urls := await self.repository.get_urls(category))
            else self.__raise_error(category)
            for category in categories
        ]
        await self.repository.add_parser_to_register(registration.categories, registration.path)
        return result

    async def delete_registration(self, category_name: list[str]) -> None:
        await self.repository.delete_parser_from_register(category_name)
