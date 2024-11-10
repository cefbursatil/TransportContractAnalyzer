from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import importlib
import sys
import os

class DataUpdateScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_update(self):
        """Schedule data updates every 6 hours"""
        self.scheduler.add_job(
            func=self.update_data,
            trigger=IntervalTrigger(hours=6),
            id='data_update_job',
            replace_existing=True
        )

    def update_data(self):
        """Execute the secop.py script to update data"""
        try:
            # Import and run the secop script
            secop = importlib.import_module('secop')
            df_secop_i, df_secop_ii = secop.fetch_and_process_all_data()
            return True
        except Exception as e:
            print(f"Error updating data: {e}")
            return False

    def force_update(self):
        """Force immediate data update"""
        return self.update_data()

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
