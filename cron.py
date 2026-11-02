# cron.py - APScheduler daily job
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import config
import report_telegram


def start_scheduler():
    scheduler = BackgroundScheduler(timezone=config.TZ)
    # Job 1: 03:00 AM - daily D1 report
    scheduler.add_job(
        report_telegram.run_daily_report,
        CronTrigger(hour=3, minute=0, timezone=config.TZ),
        args=["D1"],
        id="daily_report_03",
        replace_existing=True,
    )
    # Job 2: 07:30 AM - pre-NY H4 report
    scheduler.add_job(
        report_telegram.run_daily_report,
        CronTrigger(hour=7, minute=30, timezone=config.TZ),
        args=["H4"],
        id="pre_ny_report",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started: 03:00 (D1) + 07:30 (H4 pre-NY) " + str(config.TZ))
    return scheduler


if __name__ == "__main__":
    sched = start_scheduler()
    import time
    print("Running (Ctrl+C to stop)...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sched.shutdown()
