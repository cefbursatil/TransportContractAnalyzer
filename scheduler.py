from apscheduler.schedulers.background import BackgroundScheduler
import data_processor as dp
from datetime import datetime
import pytz

def initialize_scheduler():
    """Initialize the background scheduler for data updates"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        dp.update_data,
        'interval',
        hours=6,
        start_date=datetime.now(pytz.UTC),
        id='update_data_job'
    )
    
    try:
        scheduler.start()
    except Exception as e:
        print(f"Error starting scheduler: {e}")

if __name__ == "__main__":
    initialize_scheduler()
