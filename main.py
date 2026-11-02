# main.py - Entry point: dashboard + cron scheduler
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cron
import dashboard
import uvicorn

if __name__ == "__main__":
    scheduler = cron.start_scheduler()
    try:
        uvicorn.run(dashboard.app, host="127.0.0.1", port=8000)
    finally:
        scheduler.shutdown()
