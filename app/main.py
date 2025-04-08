import logging
import sys

from fastapi import FastAPI
from sqlalchemy import inspect

# Ensure that the models are imported so that the tables are created correctly
import app.models
from app.api import router as api_router
from app.config import settings
from app.db import Base, engine
from app.tasks.crypto_tasks import refresh_all_cryptocurrencies_metadata
from app.tasks.scheduler import schedule_periodic_task, start_scheduler

app = FastAPI()

app.include_router(api_router)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Get application logger
logger = logging.getLogger(__name__)

# Connect FastAPI logger to gunicorn's handlers (to see the logs in docker)
gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.INFO)


@app.on_event("startup")
async def initialize_db():
    """
    Initialize the database on startup (creates the tables if needed).
    """
    inspector = inspect(engine)
    # Check if all tables already exist
    if not all(
        [inspector.has_table(tablename) for tablename in Base.metadata.tables.keys()]
    ):
        logging.info("Dropping all existing database tables...")
        Base.metadata.drop_all(bind=engine)
        logging.info("Creating new database tables...")
        Base.metadata.create_all(bind=engine)
    else:
        logging.info("Database tables already exist.")


@app.on_event("startup")
async def startup_event():
    """
    Start the scheduler for periodic tasks.
    """
    start_scheduler()
    # Schedule the task to refresh all cryptocurrencies metadata every REFRESH_INTERVAL_MINUTES
    schedule_periodic_task(
        func=refresh_all_cryptocurrencies_metadata,
        interval_minutes=settings.REFRESH_INTERVAL_MINUTES,
        id="refresh_all_crypto_metadata",
        name="Refresh all cryptocurrencies metadata",
    )


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}!"}
