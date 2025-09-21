#!/usr/bin/env python3
"""
Real house listing scraper using requests and BeautifulSoup
This scrapes actual live listings from real estate websites
"""

import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
from dotenv import load_dotenv
from config import ZIP_CODES, FILTERS, EMAIL_CONFIG
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealEstateScraper:
    def __init__(self):
        self.listings = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def scrape_realtor_com(self, zip_code):
        """Scrape listings from Realtor.com"""
        try:
            logger.info(f"Scraping Realtor.com for zip code: {zip_code}")
            
            # Realtor.com search URL
            url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
            
            # Add price filters to URL
            min_price = FILTERS.get('min_price', 200000)
            max_price = FILTERS.get('max_price', 405000)
            url += f"?min_price={min_price}&max_price={max_price}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', {'data-testid': 'property-card'})
            if not listing_cards:
                # Try alternative selectors
                listing_cards = soup.find_all('div', class_=re.compile(r'property.*card|listing.*card'))
            
            logger.info(f"Found {len(listing_cards)} listing cards on Realtor.com")
            
            for card in listing_cards:
                try:
                    listing = self.extract_realtor_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting Realtor listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Realtor.com for zip {zip_code}: {e}")
    
    def extract_realtor_listing(self, card, zip_code):
        """Extract listing data from Realtor.com card"""
        try:
            listing = {
                'source': 'Realtor.com',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find('span', {'data-testid': 'property-card-price'})
            if not price_elem:
                price_elem = card.find('span', class_=re.compile(r'price|cost'))
            
            if price_elem:
                price_text = price_elem.get_text().replace('$', '').replace(',', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1))
            
            # Address
            address_elem = card.find('div', {'data-testid': 'property-card-addr'})
            if not address_elem:
                address_elem = card.find('div', class_=re.compile(r'address|location'))
            
            if address_elem:
                listing['address'] = address_elem.get_text().strip()
            
            # Property details
            details_elem = card.find('div', {'data-testid': 'property-card-details'})
            if not details_elem:
                details_elem = card.find('div', class_=re.compile(r'details|specs'))
            
            if details_elem:
                details_text = details_elem.get_text()
                
                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s*(?:bed|br|bedroom)', details_text, re.IGNORECASE)
                if bed_match:
                    listing['bedrooms'] = int(bed_match.group(1))
                
                # Extract bathrooms
                bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bath|ba|bathroom)', details_text, re.IGNORECASE)
                if bath_match:
                    listing['bathrooms'] = float(bath_match.group(1))
                
                # Extract square footage
                sqft_match = re.search(r'(\d+)\s*(?:sqft|sq\.?\s*ft)', details_text, re.IGNORECASE)
                if sqft_match:
                    listing['sqft'] = int(sqft_match.group(1))
            
            # Year built
            year_match = re.search(r'Built\s+(\d{4})', card.get_text())
            if year_match:
                listing['year_built'] = int(year_match.group(1))
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = f"https://www.realtor.com{href}"
                else:
                    listing['url'] = href
            
            # Property type
            listing['property_type'] = 'house'  # Assume house for now
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Realtor listing: {e}")
            return None
    
    def scrape_zillow(self, zip_code):
        """Scrape listings from Zillow using their API-like approach"""
        try:
            logger.info(f"Scraping Zillow for zip code: {zip_code}")
            
            # Zillow search URL
            url = f"https://www.zillow.com/homes/{zip_code}_rb/"
            
            # Add price filters
            min_price = FILTERS.get('min_price', 200000)
            max_price = FILTERS.get('max_price', 405000)
            url += f"?price={min_price}-{max_price}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', {'data-testid': 'property-card'})
            if not listing_cards:
                # Try alternative selectors
                listing_cards = soup.find_all('article', class_=re.compile(r'property|listing'))
            
            logger.info(f"Found {len(listing_cards)} listing cards on Zillow")
            
            for card in listing_cards:
                try:
                    listing = self.extract_zillow_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting Zillow listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Zillow for zip {zip_code}: {e}")
    
    def extract_zillow_listing(self, card, zip_code):
        """Extract listing data from Zillow card"""
        try:
            listing = {
                'source': 'Zillow',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find('span', {'data-testid': 'property-card-price'})
            if not price_elem:
                price_elem = card.find('span', class_=re.compile(r'price|cost'))
            
            if price_elem:
                price_text = price_elem.get_text().replace('$', '').replace(',', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1))
            
            # Address
            address_elem = card.find('address', {'data-testid': 'property-card-addr'})
            if not address_elem:
                address_elem = card.find('address', class_=re.compile(r'address|location'))
            
            if address_elem:
                listing['address'] = address_elem.get_text().strip()
            
            # Property details
            details_elem = card.find('ul', {'data-testid': 'property-card-details'})
            if not details_elem:
                details_elem = card.find('ul', class_=re.compile(r'details|specs'))
            
            if details_elem:
                details_text = details_elem.get_text()
                
                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s*(?:bd|bed|bedroom)', details_text, re.IGNORECASE)
                if bed_match:
                    listing['bedrooms'] = int(bed_match.group(1))
                
                # Extract bathrooms
                bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ba|bath|bathroom)', details_text, re.IGNORECASE)
                if bath_match:
                    listing['bathrooms'] = float(bath_match.group(1))
                
                # Extract square footage
                sqft_match = re.search(r'(\d+)\s*(?:sqft|sq\.?\s*ft)', details_text, re.IGNORECASE)
                if sqft_match:
                    listing['sqft'] = int(sqft_match.group(1))
            
            # Year built
            year_match = re.search(r'Built\s+(\d{4})', card.get_text())
            if year_match:
                listing['year_built'] = int(year_match.group(1))
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = f"https://www.zillow.com{href}"
                else:
                    listing['url'] = href
            
            # Property type
            listing['property_type'] = 'house'  # Assume house for now
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Zillow listing: {e}")
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
        logger.info(f"Starting to scrape real listings for {len(ZIP_CODES)} zip codes")
        
        for zip_code in ZIP_CODES:
            try:
                # Scrape from Realtor.com
                self.scrape_realtor_com(zip_code)
                time.sleep(2)  # Be respectful to the website
                
                # Scrape from Zillow
                self.scrape_zillow(zip_code)
                time.sleep(2)  # Be respectful to the website
                
            except Exception as e:
                logger.error(f"Error scraping zip code {zip_code}: {e}")
                continue
        
        logger.info(f"Scraping completed. Found {len(self.listings)} real listings")
    
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
                <h2>🏠 Daily House Listings Report - REAL LISTINGS</h2>
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
                    <li><strong>Zip Codes:</strong> {', '.join(ZIP_CODES)}</li>
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
            msg['Subject'] = f"Daily House Listings - {len(self.listings)} REAL houses found in Plano area"
            
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
            
            logger.info(f"Email notification sent successfully with {len(self.listings)} real listings")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    def save_to_csv(self, filename="real_house_listings.csv"):
        """Save listings to CSV file"""
        if not self.listings:
            logger.warning("No listings to save")
            return
        
        df = pd.DataFrame(self.listings)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(self.listings)} real listings to {filename}")

def main():
    """Main function for real scraping"""
    logger.info("Starting REAL house listing scraper...")
    
    try:
        scraper = RealEstateScraper()
        
        # Scrape real listings
        scraper.scrape_all_zip_codes()
        
        if scraper.listings:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_house_listings_{timestamp}.csv"
            scraper.save_to_csv(filename)
            
            # Send email notification
            scraper.send_email_notification()
            
            logger.info(f"Real scraping completed successfully! Found {len(scraper.listings)} houses")
        else:
            logger.info("No real listings found matching criteria")
            
    except Exception as e:
        logger.error(f"Error during real scraping: {e}")

if __name__ == "__main__":
    main()
