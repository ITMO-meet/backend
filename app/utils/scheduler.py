from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
from app.utils.db import db_instance

# Автоматическое удаление просроченных премом из бд

async def remove_expired_premiums():
    result = await db_instance.db["premium"].delete_many({"validUntil": {"$lt": datetime.datetime.now()}})
    print(f"removed {result.deleted_count} premium(s)")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_premiums, IntervalTrigger(hours=1))
    scheduler.start()
