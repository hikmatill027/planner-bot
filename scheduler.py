from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from handlers import request_plan, send_morning_reminder
from config import TIMEZONE

def setup_scheduler(app):
    tz = timezone(TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)

    # 10:00 PM — ask for tomorrow's plan
    scheduler.add_job(
        request_plan,
        trigger=CronTrigger(hour=22, minute=0, timezone=tz),
        kwargs={"context": app},
        id="evening_reminder",
        name="Evening Plan Request",
        replace_existing=True
    )

    # 6:00 AM — first morning reminder
    scheduler.add_job(
        send_morning_reminder,
        trigger=CronTrigger(hour=6, minute=0, timezone=tz),
        kwargs={"context": app},
        id="morning_reminder_6am",
        name="Morning Reminder 6AM",
        replace_existing=True
    )

    # 10:00 AM — second morning reminder
    scheduler.add_job(
        send_morning_reminder,
        trigger=CronTrigger(hour=10, minute=0, timezone=tz),
        kwargs={"context": app},
        id="morning_reminder_10am",
        name="Morning Reminder 10AM",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler started. Jobs registered:")
    for job in scheduler.get_jobs():
        print(f"   → {job.name} | Next run: {job.next_run_time}")

    return scheduler