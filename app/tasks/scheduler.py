# Task for automatic periodic updating of metadata via CoinGecko will be here
import atexit

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Create the scheduler
scheduler = AsyncIOScheduler()


# Function to add a periodical task to the scheduler
def schedule_periodic_task(func, interval_minutes, id, name):
    """
    Add a task to the scheduler.
    """
    scheduler.add_job(
        func=func,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id=id,
        name=name,
        replace_existing=True,
    )


# Function to start the scheduler
def start_scheduler():
    scheduler.start()
    # Register shutdown handler
    atexit.register(lambda: scheduler.shutdown())
