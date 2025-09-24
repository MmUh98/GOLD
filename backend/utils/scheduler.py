from apscheduler.triggers.cron import CronTrigger
from services.data_fetcher import insert_latest_price_if_new
from services.agents import volatility_watchdog
def register_jobs(app, scheduler):
    @scheduler.scheduled_job(CronTrigger(hour=23, minute=55))
    def job_fetch():
        with app.app_context():
            insert_latest_price_if_new()
    @scheduler.scheduled_job(CronTrigger(minute="*/10"))
    def job_alerts():
        with app.app_context():
            volatility_watchdog()
