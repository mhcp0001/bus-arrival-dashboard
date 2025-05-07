import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.services.bus_data_service import bus_data_service

logger = logging.getLogger(__name__)

class BusScheduler:
    """Scheduler for bus data fetching"""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = BackgroundScheduler()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Set up the scheduler
        self._setup_scheduler()
        
        # Register shutdown function
        app.teardown_appcontext(self._shutdown_scheduler)
    
    def _setup_scheduler(self):
        """Set up the scheduler jobs"""
        # Schedule daytime job (every 5 minutes from 6:00 to 24:00)
        self.scheduler.add_job(
            self._fetch_bus_data,
            CronTrigger(minute='*/5', hour='6-23'),
            id='daytime_fetch'
        )
        
        # Schedule nighttime job (every 15 minutes from 0:00 to 6:00)
        self.scheduler.add_job(
            self._fetch_bus_data,
            CronTrigger(minute='*/15', hour='0-5'),
            id='nighttime_fetch'
        )
        
        # Schedule a job to run at startup
        self.scheduler.add_job(
            self._fetch_bus_data,
            'date',
            run_date=datetime.now(),
            id='startup_fetch'
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("Bus data scheduler started")
    
    def _fetch_bus_data(self):
        """Fetch bus data with app context"""
        with self.app.app_context():
            try:
                logger.info("Scheduled bus data fetch triggered")
                success = bus_data_service.fetch_all_bus_data()
                if success:
                    logger.info("Scheduled bus data fetch completed successfully")
                else:
                    logger.warning("Scheduled bus data fetch completed with errors")
            except Exception as e:
                logger.error(f"Error in scheduled bus data fetch: {str(e)}")
    
    def _shutdown_scheduler(self, exception=None):
        """Shut down the scheduler when the app context tears down"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Bus data scheduler shutdown")


# Create an instance of the scheduler
bus_scheduler = BusScheduler()