#!/usr/bin/env python3
"""
Advanced house listing scraper with multiple strategies
Uses different approaches to get real listings from various sources
"""

import requests
import pandas as pd
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import json
from dotenv import load_dotenv
from config import ZIP_CODES, FILTERS, EMAIL_CONFIG
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedRealEstateScraper:
    def __init__(self):
        self.listings = []
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.update_session()
    
    def update_session(self):
        """Update session with random user agent and headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_homes_com(self, zip_code):
        """Scrape listings from Homes.com"""
        try:
            logger.info(f"Scraping Homes.com for zip code: {zip_code}")
            
            # Homes.com search URL
            url = f"https://www.homes.com/{zip_code}/homes-for-sale/"
            
            # Add price filters
            min_price = FILTERS.get('min_price', 200000)
            max_price = FILTERS.get('max_price', 405000)
            url += f"?minprice={min_price}&maxprice={max_price}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', class_=re.compile(r'property.*card|listing.*card|home.*card'))
            
            logger.info(f"Found {len(listing_cards)} listing cards on Homes.com")
            
            for card in listing_cards:
                try:
                    listing = self.extract_homes_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting Homes.com listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Homes.com for zip {zip_code}: {e}")
    
    def extract_homes_listing(self, card, zip_code):
        """Extract listing data from Homes.com card"""
        try:
            listing = {
                'source': 'Homes.com',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find('span', class_=re.compile(r'price|cost|amount'))
            if not price_elem:
                price_elem = card.find('div', class_=re.compile(r'price|cost|amount'))
            
            if price_elem:
                price_text = price_elem.get_text().replace('$', '').replace(',', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1))
            
            # Address
            address_elem = card.find('div', class_=re.compile(r'address|location|street'))
            if not address_elem:
                address_elem = card.find('h3', class_=re.compile(r'address|location|street'))
            
            if address_elem:
                listing['address'] = address_elem.get_text().strip()
            
            # Property details
            details_text = card.get_text()
            
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
            year_match = re.search(r'Built\s+(\d{4})', details_text)
            if year_match:
                listing['year_built'] = int(year_match.group(1))
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = f"https://www.homes.com{href}"
                else:
                    listing['url'] = href
            
            # Property type
            listing['property_type'] = 'house'
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Homes.com listing: {e}")
            return None
    
    def scrape_trulia(self, zip_code):
        """Scrape listings from Trulia"""
        try:
            logger.info(f"Scraping Trulia for zip code: {zip_code}")
            
            # Trulia search URL
            url = f"https://www.trulia.com/for_sale/{zip_code}_zip/"
            
            # Add price filters
            min_price = FILTERS.get('min_price', 200000)
            max_price = FILTERS.get('max_price', 405000)
            url += f"?price={min_price},{max_price}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', class_=re.compile(r'property.*card|listing.*card|home.*card'))
            
            logger.info(f"Found {len(listing_cards)} listing cards on Trulia")
            
            for card in listing_cards:
                try:
                    listing = self.extract_trulia_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting Trulia listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Trulia for zip {zip_code}: {e}")
    
    def extract_trulia_listing(self, card, zip_code):
        """Extract listing data from Trulia card"""
        try:
            listing = {
                'source': 'Trulia',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find('div', class_=re.compile(r'price|cost|amount'))
            if not price_elem:
                price_elem = card.find('span', class_=re.compile(r'price|cost|amount'))
            
            if price_elem:
                price_text = price_elem.get_text().replace('$', '').replace(',', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1))
            
            # Address
            address_elem = card.find('div', class_=re.compile(r'address|location|street'))
            if not address_elem:
                address_elem = card.find('h3', class_=re.compile(r'address|location|street'))
            
            if address_elem:
                listing['address'] = address_elem.get_text().strip()
            
            # Property details
            details_text = card.get_text()
            
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
            year_match = re.search(r'Built\s+(\d{4})', details_text)
            if year_match:
                listing['year_built'] = int(year_match.group(1))
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = f"https://www.trulia.com{href}"
                else:
                    listing['url'] = href
            
            # Property type
            listing['property_type'] = 'house'
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Trulia listing: {e}")
            return None
    
    def scrape_apartments_com(self, zip_code):
        """Scrape house listings from Apartments.com (they also have houses)"""
        try:
            logger.info(f"Scraping Apartments.com for zip code: {zip_code}")
            
            # Apartments.com search URL for houses
            url = f"https://www.apartments.com/houses/{zip_code}/"
            
            # Add price filters
            min_price = FILTERS.get('min_price', 200000)
            max_price = FILTERS.get('max_price', 405000)
            url += f"?minRent={min_price}&maxRent={max_price}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find listing cards
            listing_cards = soup.find_all('div', class_=re.compile(r'property.*card|listing.*card|home.*card'))
            
            logger.info(f"Found {len(listing_cards)} listing cards on Apartments.com")
            
            for card in listing_cards:
                try:
                    listing = self.extract_apartments_listing(card, zip_code)
                    if listing and self.matches_filters(listing):
                        self.listings.append(listing)
                except Exception as e:
                    logger.warning(f"Error extracting Apartments.com listing: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Apartments.com for zip {zip_code}: {e}")
    
    def extract_apartments_listing(self, card, zip_code):
        """Extract listing data from Apartments.com card"""
        try:
            listing = {
                'source': 'Apartments.com',
                'zip_code': zip_code,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Price
            price_elem = card.find('span', class_=re.compile(r'price|cost|amount|rent'))
            if not price_elem:
                price_elem = card.find('div', class_=re.compile(r'price|cost|amount|rent'))
            
            if price_elem:
                price_text = price_elem.get_text().replace('$', '').replace(',', '')
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1))
            
            # Address
            address_elem = card.find('div', class_=re.compile(r'address|location|street'))
            if not address_elem:
                address_elem = card.find('h3', class_=re.compile(r'address|location|street'))
            
            if address_elem:
                listing['address'] = address_elem.get_text().strip()
            
            # Property details
            details_text = card.get_text()
            
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
            year_match = re.search(r'Built\s+(\d{4})', details_text)
            if year_match:
                listing['year_built'] = int(year_match.group(1))
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = f"https://www.apartments.com{href}"
                else:
                    listing['url'] = href
            
            # Property type
            listing['property_type'] = 'house'
            
            return listing
            
        except Exception as e:
            logger.warning(f"Error extracting Apartments.com listing: {e}")
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
                # Update session with new user agent
                self.update_session()
                
                # Try different sources
                self.scrape_homes_com(zip_code)
                time.sleep(random.uniform(2, 4))  # Random delay
                
                self.scrape_trulia(zip_code)
                time.sleep(random.uniform(2, 4))  # Random delay
                
                self.scrape_apartments_com(zip_code)
                time.sleep(random.uniform(2, 4))  # Random delay
                
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
    """Main function for advanced real scraping"""
    logger.info("Starting ADVANCED real house listing scraper...")
    
    try:
        scraper = AdvancedRealEstateScraper()
        
        # Scrape real listings
        scraper.scrape_all_zip_codes()
        
        if scraper.listings:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"real_house_listings_{timestamp}.csv"
            scraper.save_to_csv(filename)
            
            # Send email notification
            scraper.send_email_notification()
            
            logger.info(f"Advanced scraping completed successfully! Found {len(scraper.listings)} houses")
        else:
            logger.info("No real listings found matching criteria")
            
    except Exception as e:
        logger.error(f"Error during advanced scraping: {e}")

if __name__ == "__main__":
    main()
