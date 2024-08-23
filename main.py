from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.logger import configure_logging
from app.api.routers import main_router
from app.scheduler import Scheduler


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_):
    configure_logging(write_logger_level=logging.WARNING, stream_logger_level=logging.INFO)
    scheduler = Scheduler()
    await scheduler.start()
    yield
    await scheduler.shutdown()


app = FastAPI(lifespan=lifespan, title="Builder links")
app.include_router(main_router)
