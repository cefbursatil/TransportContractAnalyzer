from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import importlib
import sys
import os
import pandas as pd
from .data_processor import DataProcessor
import logging

logger = logging.getLogger(__name__)

class DataUpdateScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.last_data = None
        self.notification_recipients = []

    def schedule_update(self):
        """Schedule data updates every 6 hours"""
        self.scheduler.add_job(
            func=self.update_data,
            trigger=IntervalTrigger(hours=6),
            id='data_update_job',
            replace_existing=True
        )

    def set_notification_recipients(self, recipients):
        """Set email recipients for notifications"""
        self.notification_recipients = recipients

    def update_data(self):
        """Execute the secop.py script to update data and check for new contracts"""
        try:
            # Import and run the secop script
            secop = importlib.import_module('secop')
            current_active_df, current_presentation_df = secop.fetch_and_process_all_data()

            # Process the current data
            processor = DataProcessor()
            current_active_df = processor.process_contracts(current_active_df, 'active')
            
            # If we have previous data and notification recipients
            if self.last_data is not None and self.notification_recipients:
                processor.notify_if_new_contracts(
                    current_active_df,
                    self.last_data,
                    self.notification_recipients
                )

            # Update last_data
            self.last_data = current_active_df
            
            return True
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            return False

    def force_update(self):
        """Force immediate data update"""
        return self.update_data()

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
