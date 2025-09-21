"""
House listing scraper that fetches listings from multiple real estate websites
"""

import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import ZIP_CODES, FILTERS, REQUEST_DELAY, MAX_RETRIES, EMAIL_CONFIG
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HouseListingScraper:
    def __init__(self):
        self.listings = []
        self.setup_driver()
    
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # For GitHub Actions, use the system Chrome
        if os.getenv('GITHUB_ACTIONS'):
            chrome_options.binary_location = "/usr/bin/google-chrome"
            service = Service(ChromeDriverManager().install())
        else:
            service = Service(ChromeDriverManager().install())
            
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def scrape_zillow(self, zip_code):
        """Scrape listings from Zillow for a specific zip code"""
        try:
            url = f"https://www.zillow.com/homes/{zip_code}_rb/"
            logger.info(f"Scraping Zillow for zip code: {zip_code}")
            
            self.driver.get(url)
            time.sleep(REQUEST_DELAY)
            
            # Apply filters if possible
            self.apply_zillow_filters()
            
            # Wait for listings to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='property-card']")))
            
            # Scroll to load more listings
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find all listing cards
            listing_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-card']")
            
            for card in listing_cards:
                try:
                    listing = self.extract_zillow_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting listing from Zillow: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Zillow for zip {zip_code}: {e}")
    
    def apply_zillow_filters(self):
        """Apply filters on Zillow search page"""
        try:
            # Click on filters button
            filter_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='filter-button']")
            filter_button.click()
            time.sleep(1)
            
            # Set price range
            if FILTERS.get('min_price'):
                min_price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='min-price-input']")
                min_price_input.clear()
                min_price_input.send_keys(str(FILTERS['min_price']))
            
            if FILTERS.get('max_price'):
                max_price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='max-price-input']")
                max_price_input.clear()
                max_price_input.send_keys(str(FILTERS['max_price']))
            
            # Apply filters
            apply_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='apply-filters-button']")
            apply_button.click()
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"Could not apply Zillow filters: {e}")
    
    def extract_zillow_listing(self, card, zip_code):
        """Extract listing data from a Zillow property card"""
        try:
            listing = {
                'source': 'Zillow',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-price']")
            price_text = price_elem.text.replace('$', '').replace(',', '')
            listing['price'] = int(re.findall(r'\d+', price_text)[0]) if re.findall(r'\d+', price_text) else None
            
            # Address
            address_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-addr']")
            listing['address'] = address_elem.text
            
            # Bedrooms, Bathrooms, Square Feet
            details = card.find_elements(By.CSS_SELECTOR, "[data-testid='property-card-details'] span")
            for detail in details:
                text = detail.text
                if 'bd' in text:
                    listing['bedrooms'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
                elif 'ba' in text:
                    listing['bathrooms'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
                elif 'sqft' in text:
                    listing['sqft'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
            
            # Year built (if available)
            try:
                year_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-year-built']")
                listing['year_built'] = int(re.findall(r'\d{4}', year_elem.text)[0]) if re.findall(r'\d{4}', year_elem.text) else None
            except:
                listing['year_built'] = None
            
            # URL
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a[data-testid='property-card-link']")
                listing['url'] = link_elem.get_attribute('href')
            except:
                listing['url'] = None
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Zillow listing: {e}")
            return None
    
    def scrape_realtor(self, zip_code):
        """Scrape listings from Realtor.com for a specific zip code"""
        try:
            url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
            logger.info(f"Scraping Realtor.com for zip code: {zip_code}")
            
            self.driver.get(url)
            time.sleep(REQUEST_DELAY)
            
            # Apply filters
            self.apply_realtor_filters()
            
            # Wait for listings to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='property-card']")))
            
            # Find all listing cards
            listing_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-card']")
            
            for card in listing_cards:
                try:
                    listing = self.extract_realtor_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting listing from Realtor: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Realtor.com for zip {zip_code}: {e}")
    
    def apply_realtor_filters(self):
        """Apply filters on Realtor.com search page"""
        try:
            # Click on filters button
            filter_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='filter-button']")
            filter_button.click()
            time.sleep(1)
            
            # Set price range
            if FILTERS.get('min_price'):
                min_price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='min-price-input']")
                min_price_input.clear()
                min_price_input.send_keys(str(FILTERS['min_price']))
            
            if FILTERS.get('max_price'):
                max_price_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='max-price-input']")
                max_price_input.clear()
                max_price_input.send_keys(str(FILTERS['max_price']))
            
            # Apply filters
            apply_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='apply-filters-button']")
            apply_button.click()
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"Could not apply Realtor filters: {e}")
    
    def extract_realtor_listing(self, card, zip_code):
        """Extract listing data from a Realtor.com property card"""
        try:
            listing = {
                'source': 'Realtor.com',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-price']")
            price_text = price_elem.text.replace('$', '').replace(',', '')
            listing['price'] = int(re.findall(r'\d+', price_text)[0]) if re.findall(r'\d+', price_text) else None
            
            # Address
            address_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-addr']")
            listing['address'] = address_elem.text
            
            # Bedrooms, Bathrooms, Square Feet
            details = card.find_elements(By.CSS_SELECTOR, "[data-testid='property-card-details'] span")
            for detail in details:
                text = detail.text
                if 'bd' in text:
                    listing['bedrooms'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
                elif 'ba' in text:
                    listing['bathrooms'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
                elif 'sqft' in text:
                    listing['sqft'] = int(re.findall(r'\d+', text)[0]) if re.findall(r'\d+', text) else None
            
            # Year built (if available)
            try:
                year_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='property-card-year-built']")
                listing['year_built'] = int(re.findall(r'\d{4}', year_elem.text)[0]) if re.findall(r'\d{4}', year_elem.text) else None
            except:
                listing['year_built'] = None
            
            # URL
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a[data-testid='property-card-link']")
                listing['url'] = link_elem.get_attribute('href')
            except:
                listing['url'] = None
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Realtor listing: {e}")
            return None
    
    def matches_filters(self, listing):
        """Check if a listing matches the specified filters"""
        if not listing.get('price'):
            return False
        
        # Price filter
        if listing['price'] < FILTERS.get('min_price', 0) or listing['price'] > FILTERS.get('max_price', float('inf')):
            return False
        
        # Year built filter
        if listing.get('year_built'):
            if listing['year_built'] < FILTERS.get('min_year_built', 0) or listing['year_built'] > FILTERS.get('max_year_built', 9999):
                return False
        
        # Square footage filter
        if listing.get('sqft'):
            if listing['sqft'] < FILTERS.get('min_sqft', 0) or listing['sqft'] > FILTERS.get('max_sqft', float('inf')):
                return False
        
        # Bedrooms filter
        if listing.get('bedrooms'):
            if listing['bedrooms'] < FILTERS.get('bedrooms', 0):
                return False
        
        # Bathrooms filter
        if listing.get('bathrooms'):
            if listing['bathrooms'] < FILTERS.get('bathrooms', 0):
                return False
        
        # Property type filter - exclude townhomes
        if listing.get('property_type'):
            property_type = listing['property_type'].lower()
            if 'townhouse' in property_type or 'townhome' in property_type or 'condo' in property_type:
                return False
        
        return True
    
    def scrape_all_zip_codes(self):
        """Scrape listings from all configured zip codes"""
        logger.info(f"Starting to scrape listings for {len(ZIP_CODES)} zip codes")
        
        for zip_code in ZIP_CODES:
            try:
                # Scrape from Zillow
                self.scrape_zillow(zip_code)
                time.sleep(REQUEST_DELAY)
                
                # Scrape from Realtor.com
                self.scrape_realtor(zip_code)
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Error scraping zip code {zip_code}: {e}")
                continue
        
        logger.info(f"Scraping completed. Found {len(self.listings)} listings")
    
    def save_to_csv(self, filename="house_listings.csv"):
        """Save listings to CSV file"""
        if not self.listings:
            logger.warning("No listings to save")
            return
        
        df = pd.DataFrame(self.listings)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(self.listings)} listings to {filename}")
    
    def send_email_notification(self):
        """Send email notification with house listings"""
        if not self.listings:
            logger.info("No listings to send via email")
            return
        
        # Get email password from environment variable
        email_password = os.getenv('EMAIL_PASSWORD')
        if not email_password:
            logger.warning("EMAIL_PASSWORD environment variable not set. Skipping email notification.")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['recipient_email']
            msg['Subject'] = f"Daily House Listings - {len(self.listings)} houses found"
            
            # Create HTML body with house listings
            html_body = self.create_email_html()
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], email_password)
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
            server.quit()
            
            logger.info(f"Email notification sent successfully with {len(self.listings)} listings")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def create_email_html(self):
        """Create HTML email body with house listings"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .listing {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .price {{ font-size: 18px; font-weight: bold; color: #2c5aa0; }}
                .address {{ font-size: 16px; color: #333; margin: 5px 0; }}
                .details {{ color: #666; margin: 5px 0; }}
                .url {{ margin-top: 10px; }}
                .url a {{ color: #2c5aa0; text-decoration: none; }}
                .url a:hover {{ text-decoration: underline; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🏠 Daily House Listings Report</h2>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Total Houses Found:</strong> {len(self.listings)}</p>
            </div>
            
            <div class="summary">
                <h3>Search Criteria:</h3>
                <ul>
                    <li><strong>Price Range:</strong> ${FILTERS['min_price']:,} - ${FILTERS['max_price']:,}</li>
                    <li><strong>Year Built:</strong> {FILTERS['min_year_built']} - {FILTERS['max_year_built']}</li>
                    <li><strong>Property Type:</strong> Houses only (no townhomes/condos)</li>
                    <li><strong>Minimum Bedrooms:</strong> {FILTERS['bedrooms']}</li>
                    <li><strong>Minimum Bathrooms:</strong> {FILTERS['bathrooms']}</li>
                </ul>
            </div>
        """
        
        for i, listing in enumerate(self.listings, 1):
            price = f"${listing.get('price', 'N/A'):,}" if listing.get('price') else 'N/A'
            address = listing.get('address', 'N/A')
            bedrooms = listing.get('bedrooms', 'N/A')
            bathrooms = listing.get('bathrooms', 'N/A')
            sqft = f"{listing.get('sqft', 'N/A'):,}" if listing.get('sqft') else 'N/A'
            year_built = listing.get('year_built', 'N/A')
            url = listing.get('url', '#')
            source = listing.get('source', 'Unknown')
            
            html += f"""
            <div class="listing">
                <div class="price">{price}</div>
                <div class="address">{address}</div>
                <div class="details">
                    <strong>Details:</strong> {bedrooms} bed, {bathrooms} bath, {sqft} sqft
                    {f", Built: {year_built}" if year_built != 'N/A' else ""}
                    <br><strong>Source:</strong> {source}
                </div>
                <div class="url">
                    <a href="{url}" target="_blank">View Listing</a>
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def close(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
