from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class RedisConfig(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db_name: str
    redis_password: str | None = None


class NotifyConfig(BaseSettings):
    notify_host: str
    notify_port: int
    notify_path: str
    protocol: str = "http"

    @property
    def notify_url(self):
        if self.notify_port in [443, 8443]:
            self.protocol = "https"
        return f"{self.protocol}://{self.notify_host}:{self.notify_port}{self.notify_path}"


class Settings(BaseSettings):
    min_count_for_sort: int
    max_count_for_sort: int
    min_count_for_filter: int
    chunk_size: int
    sleep_between_request: int | float
    sleep_between_chunk: int | float
    use_notify_send: bool
    use_notify_log: bool
    time_create_urls: int
    notify_config: NotifyConfig = NotifyConfig()


settings = Settings()
