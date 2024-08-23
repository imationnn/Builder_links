import zoneinfo
import datetime
import logging

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from app.client import Builder
from app.repository.redis_storage import RedisStorage, RedisClient
from app.config.settings import settings, RedisConfig


logger = logging.getLogger(__name__)


async def start_get_urls(repository: RedisStorage, builder: Builder):
    categories = await repository.get_categories_for_parsing()
    if not categories:
        logger.warning("No registered parsers, next check in %s hours", settings.time_create_urls)
        return
    await builder.build(categories)
    await builder.send_urls_to_registered_parsers()


class Scheduler:
    def __init__(self):
        self.job_store = "default"
        self.id_job_get_urls = "get_urls"
        self.scheduler = ContextSchedulerDecorator(
            AsyncIOScheduler(
                jobstores={self.job_store: RedisJobStore(host=RedisConfig().redis_host)},
                timezone=zoneinfo.ZoneInfo("Europe/Moscow")
            )
        )
        self.redis_client = RedisClient()
        self.repository = RedisStorage(self.redis_client.redis)
        self.builder = Builder(self.repository)
        self.scheduler.ctx.add_instance(self.repository, RedisStorage)
        self.scheduler.ctx.add_instance(self.redis_client, RedisClient)
        self.scheduler.ctx.add_instance(self.builder, Builder)

    def add_job_start_get_urls(self):
        self.scheduler.add_job(
            start_get_urls,
            'interval',
            id=self.id_job_get_urls,
            hours=settings.time_create_urls,
            misfire_grace_time=300,
            next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=10)
        )

    async def start(self):
        self.scheduler.start()
        job = self.scheduler.get_job(self.id_job_get_urls, self.job_store)
        if not job:
            self.add_job_start_get_urls()
        else:
            logger.info("Job %s scheduled at %s", job.name, job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'))

    async def shutdown(self):
        self.scheduler.shutdown()
        await self.redis_client.close()
