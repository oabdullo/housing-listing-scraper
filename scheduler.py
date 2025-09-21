"""
Daily job scheduler for house listing scraper
Runs the scraper every day at 8:00 AM
"""

import schedule
import time
import logging
from datetime import datetime
from zillow56_scraper import Zillow56Scraper
from config import SCHEDULE_TIME, OUTPUT_FILE, LOG_FILE
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HouseListingScheduler:
    def __init__(self):
        self.scraper = None
        self.email_config = self.load_email_config()
    
    def load_email_config(self):
        """Load email configuration from environment variables or config file"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'email': os.getenv('EMAIL_ADDRESS', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'recipient': os.getenv('RECIPIENT_EMAIL', '')
        }
    
    def run_daily_scrape(self):
        """Run the daily house listing scrape"""
        logger.info("Starting daily house listing scrape...")
        
        try:
            # Initialize scraper
            self.scraper = Zillow56Scraper()
            
            # Run the scrape
            listings = self.scraper.search_plano_houses()
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"house_listings_{timestamp}.csv"
            self.scraper.save_to_csv(filename)
            
            # Send notification email
            self.scraper.send_email_notification()
            
            logger.info(f"Daily scrape completed successfully. Found {len(self.scraper.listings)} listings.")
            
        except Exception as e:
            logger.error(f"Error during daily scrape: {e}")
            self.send_error_notification(str(e))
        
        finally:
            if self.scraper:
                self.scraper.close()
    
    def send_notification_email(self, filename, listing_count):
        """Send email notification with results"""
        if not all([self.email_config['email'], self.email_config['password'], self.email_config['recipient']]):
            logger.warning("Email configuration incomplete. Skipping email notification.")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"Daily House Listings - {listing_count} new listings found"
            
            body = f"""
            Daily House Listing Report
            
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Total Listings Found: {listing_count}
            
            The CSV file with all listings has been attached.
            
            Best regards,
            House Listing Scraper
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file
            if os.path.exists(filename):
                with open(filename, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}',
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['email'], self.email_config['recipient'], text)
            server.quit()
            
            logger.info("Notification email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending notification email: {e}")
    
    def send_error_notification(self, error_message):
        """Send error notification email"""
        if not all([self.email_config['email'], self.email_config['password'], self.email_config['recipient']]):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = "House Listing Scraper - Error Alert"
            
            body = f"""
            House Listing Scraper Error Alert
            
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Error: {error_message}
            
            Please check the logs for more details.
            
            Best regards,
            House Listing Scraper
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['email'], self.email_config['recipient'], text)
            server.quit()
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        logger.info(f"Starting scheduler - will run daily at {SCHEDULE_TIME}")
        
        # Schedule the job
        schedule.every().day.at(SCHEDULE_TIME).do(self.run_daily_scrape)
        
        # Run immediately for testing (optional)
        # self.run_daily_scrape()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run the scraper once (for testing)"""
        logger.info("Running scraper once...")
        self.run_daily_scrape()

if __name__ == "__main__":
    scheduler = HouseListingScheduler()
    
    # Check if running with --once flag for testing
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        scheduler.run_once()
    else:
        scheduler.start_scheduler()
