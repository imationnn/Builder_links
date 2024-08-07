from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class RedisConfig(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db_name: str
    redis_password: str | None = None
