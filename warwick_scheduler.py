"""
Daily job scheduler for Warwick NY house listing scraper
Runs the Warwick scraper every day at 9:00 AM (1 hour after Plano scraper)
"""

import schedule
import time
import logging
from datetime import datetime
from zillow56_scraper import Zillow56Scraper
from config import SCHEDULE_TIME, OUTPUT_FILE, LOG_FILE
import os

# Set up logging for Warwick scraper
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('warwick_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WarwickHouseListingScheduler:
    def __init__(self):
        self.scraper = None
    
    def run_daily_scrape(self):
        """Run the daily Warwick NY house listing scrape"""
        logger.info("Starting daily Warwick NY house listing scrape...")
        
        try:
            # Initialize scraper
            self.scraper = Zillow56Scraper()
            
            # Run the Warwick scrape
            listings = self.scraper.search_warwick_houses()
            
            if not listings:
                logger.warning("No Warwick NY listings found matching criteria")
                return
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"warwick_listings_{timestamp}.csv"
            self.scraper.save_to_csv(filename)
            
            # Send notification email to both recipients
            self.scraper.send_email_notification(test_mode=False)
            
            logger.info(f"Warwick NY scrape completed successfully. Found {len(self.scraper.listings)} listings.")
            
        except Exception as e:
            logger.error(f"Error during Warwick NY daily scrape: {e}")
        
        finally:
            if self.scraper:
                # Clean up if needed
                pass
    
    def start_scheduler(self):
        """Start the daily scheduler for Warwick NY"""
        logger.info("Starting Warwick NY scheduler - will run daily at 09:00")
        
        # Schedule the job for 9:00 AM (1 hour after Plano scraper)
        schedule.every().day.at("09:00").do(self.run_daily_scrape)
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run the Warwick scraper once (for testing)"""
        logger.info("Running Warwick NY scraper once...")
        self.run_daily_scrape()

if __name__ == "__main__":
    scheduler = WarwickHouseListingScheduler()
    
    # Check if running with --once flag for testing
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        scheduler.run_once()
    else:
        scheduler.start_scheduler()
