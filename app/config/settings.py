from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class RedisConfig(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db_name: str
    redis_password: str | None = None


class Settings(BaseSettings):
    min_count_for_sort: int
    max_count_for_sort: int
    min_count_for_filter: int
    chunk_size: int
    sleep_between_request: int | float
    sleep_between_chunk: int | float


settings = Settings()
