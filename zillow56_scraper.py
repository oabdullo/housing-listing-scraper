#!/usr/bin/env python3
"""
Zillow56 API Scraper - Optimized for single daily request
Uses RapidAPI Zillow56 to search for Plano area houses meeting criteria
"""

import requests
import json
import csv
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import ZIP_CODES, FILTERS, EMAIL_CONFIG

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class Zillow56Scraper:
    """Zillow56 API scraper optimized for single daily request"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = 'https://zillow56.p.rapidapi.com'
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'zillow56.p.rapidapi.com'
        }
        self.listings = []
        
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY not found in environment variables")
    
    def search_plano_houses(self):
        """
        Single optimized search for Plano area houses
        Combines all zip codes into one comprehensive search
        """
        logging.info("Starting single Zillow56 search for Plano area houses")
        
        try:
            # Create a comprehensive search query for Plano area
            # Using the main Plano zip code (75024) as the primary search
            # This should capture houses in the broader Plano area
            url = f"{self.base_url}/search"
            
            # Build comprehensive search parameters
            params = {
                'location': 'Plano, TX',  # Primary location
                'home_type': 'Houses',    # Only houses
                'min_price': FILTERS['min_price'],
                'max_price': FILTERS['max_price'],
                'min_bedrooms': FILTERS['bedrooms'],
                'min_bathrooms': FILTERS['bathrooms'],
                'min_sqft': FILTERS['min_sqft'],
                'max_sqft': FILTERS['max_sqft'],
                'min_year_built': FILTERS['min_year_built'],
                'max_year_built': FILTERS['max_year_built'],
                'sort': 'newest',  # Get newest listings
                'limit': 50  # Maximum results per request
            }
            
            logging.info(f"Searching with parameters: {params}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ API call successful! Status: {response.status_code}")
                
                # Extract listings from response
                listings = self._extract_listings(data)
                self.listings = listings
                
                logging.info(f"Found {len(listings)} houses matching criteria")
                return listings
                
            else:
                logging.error(f"API call failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Error in search_plano_houses: {e}")
            return []
    
    def _extract_listings(self, data):
        """Extract and format listings from API response"""
        listings = []
        
        try:
            # The response structure may vary, so we'll handle different formats
            results = []
            
            if isinstance(data, dict):
                # Try different possible keys for results
                if 'results' in data:
                    results = data['results']
                elif 'listings' in data:
                    results = data['listings']
                elif 'properties' in data:
                    results = data['properties']
                elif 'homes' in data:
                    results = data['homes']
                elif 'data' in data:
                    results = data['data']
                else:
                    # If it's a single property or different structure
                    results = [data] if data else []
            elif isinstance(data, list):
                results = data
            
            logging.info(f"Processing {len(results)} raw results from API")
            
            for item in results:
                try:
                    listing = self._format_listing(item)
                    if listing and self._matches_filters(listing):
                        listings.append(listing)
                        logging.info(f"Added listing: {listing['address']} - ${listing['price']:,}")
                except Exception as e:
                    logging.error(f"Error processing listing: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            logging.error(f"Error extracting listings: {e}")
            return []
    
    def _format_listing(self, item):
        """Format a single listing from API response"""
        try:
            # Extract basic information
            address = item.get('address', item.get('streetAddress', 'N/A'))
            city = item.get('city', 'Plano')
            state = item.get('state', 'TX')
            zip_code = item.get('zipCode', item.get('zipcode', '75024'))
            
            # Price information
            price = item.get('price', item.get('listPrice', 0))
            if isinstance(price, str):
                price = int(price.replace('$', '').replace(',', ''))
            
            # Property details
            bedrooms = item.get('bedrooms', item.get('beds', 0))
            bathrooms = item.get('bathrooms', item.get('baths', 0))
            sqft = item.get('livingArea', item.get('squareFeet', item.get('sqft', 0)))
            year_built = item.get('yearBuilt', item.get('yearBuilt', 0))
            
            # URL
            url = item.get('url', item.get('detailUrl', item.get('hdpUrl', 'N/A')))
            if url and not url.startswith('http'):
                url = f"https://www.zillow.com{url}"
            
            # Zestimate
            zestimate = item.get('zestimate', item.get('estimatedValue', 0))
            if isinstance(zestimate, str):
                zestimate = int(zestimate.replace('$', '').replace(',', ''))
            
            return {
                'address': f"{address}, {city}, {state} {zip_code}",
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'sqft': sqft,
                'year_built': year_built,
                'home_type': 'house',
                'url': url,
                'zestimate': zestimate,
                'zip_code': zip_code,
                'source': 'Zillow56 API'
            }
            
        except Exception as e:
            logging.error(f"Error formatting listing: {e}")
            return None
    
    def _matches_filters(self, listing):
        """Check if listing matches our filters"""
        try:
            # Price filter
            price = listing.get('price', 0)
            if price < FILTERS['min_price'] or price > FILTERS['max_price']:
                return False
            
            # Year built filter
            year_built = listing.get('year_built', 0)
            if year_built > 0 and (year_built < FILTERS['min_year_built'] or year_built > FILTERS['max_year_built']):
                return False
            
            # Square footage filter
            sqft = listing.get('sqft', 0)
            if sqft > 0 and (sqft < FILTERS['min_sqft'] or sqft > FILTERS['max_sqft']):
                return False
            
            # Bedrooms filter
            bedrooms = listing.get('bedrooms', 0)
            if bedrooms < FILTERS['bedrooms']:
                return False
            
            # Bathrooms filter
            bathrooms = listing.get('bathrooms', 0)
            if bathrooms < FILTERS['bathrooms']:
                return False
            
            # Property type filter
            home_type = listing.get('home_type', '').lower()
            if any(excluded in home_type for excluded in ['townhouse', 'townhome', 'condo', 'apartment']):
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking filters: {e}")
            return False
    
    def save_to_csv(self, filename=None):
        """Save listings to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"house_listings_{timestamp}.csv"
        
        if not self.listings:
            logging.warning("No listings to save")
            return None
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['address', 'price', 'bedrooms', 'bathrooms', 'sqft', 
                             'year_built', 'home_type', 'url', 'zestimate', 'zip_code', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for listing in self.listings:
                    writer.writerow(listing)
            
            logging.info(f"Saved {len(self.listings)} listings to {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"Error saving to CSV: {e}")
            return None
    
    def send_email_notification(self):
        """Send email notification with listings (no Chrome required)"""
        try:
            if not self.listings:
                logging.warning("No listings to send in email")
                return
            
            # Get email password from environment
            email_password = os.getenv('EMAIL_PASSWORD')
            if not email_password:
                logging.error("EMAIL_PASSWORD not found in environment variables")
                return
            
            # Create email content
            subject = f"🏠 Daily House Listings - {len(self.listings)} Houses Found"
            
            # Create HTML email body
            html_body = self._create_email_html()
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['recipient_email']
            
            # Attach HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['sender_email'], email_password)
                server.send_message(msg)
            
            logging.info(f"✅ Email sent successfully to {EMAIL_CONFIG['recipient_email']}")
            
        except Exception as e:
            logging.error(f"Error sending email: {e}")
    
    def _create_email_html(self):
        """Create HTML email content"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .listing {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .price {{ font-size: 18px; font-weight: bold; color: #2c5aa0; }}
                .address {{ font-size: 16px; color: #333; }}
                .details {{ color: #666; margin: 5px 0; }}
                .url {{ margin-top: 10px; }}
                .url a {{ color: #2c5aa0; text-decoration: none; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏠 Daily House Listings - Plano Area</h1>
                <p>Found <strong>{len(self.listings)}</strong> houses matching your criteria</p>
                <p>Search Criteria: ${FILTERS['min_price']:,} - ${FILTERS['max_price']:,}, {FILTERS['bedrooms']}+ beds, {FILTERS['bathrooms']}+ baths, {FILTERS['min_sqft']}+ sqft</p>
            </div>
        """
        
        for i, listing in enumerate(self.listings, 1):
            price = f"${listing['price']:,.0f}"
            address = listing['address']
            bedrooms = listing['bedrooms']
            bathrooms = listing['bathrooms']
            sqft = f"{listing['sqft']:,.0f}" if listing['sqft'] > 0 else "N/A"
            year_built = listing['year_built'] if listing['year_built'] > 0 else "N/A"
            url = listing['url'] if listing['url'] != 'https://www.zillow.comN/A' else "N/A"
            
            html += f"""
            <div class="listing">
                <div class="price">{price}</div>
                <div class="address">{address}</div>
                <div class="details">
                    <strong>Bedrooms:</strong> {bedrooms} | 
                    <strong>Bathrooms:</strong> {bathrooms} | 
                    <strong>Square Feet:</strong> {sqft} | 
                    <strong>Year Built:</strong> {year_built}
                </div>
                <div class="url">
                    <a href="{url}" target="_blank">View on Zillow →</a>
                </div>
            </div>
            """
        
        html += """
            <div class="summary">
                <p><strong>Source:</strong> Zillow56 API via RapidAPI</p>
                <p><strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
        </body>
        </html>
        """
        
        return html

def main():
    """Main function to run the scraper"""
    try:
        # Initialize scraper
        scraper = Zillow56Scraper()
        
        # Make single optimized search
        listings = scraper.search_plano_houses()
        
        if not listings:
            logging.warning("No listings found matching criteria")
            return
        
        # Save to CSV
        csv_file = scraper.save_to_csv()
        
        # Send email notification (no Chrome required)
        scraper.send_email_notification()
        
        logging.info(f"Zillow56 scraping completed successfully! Found {len(listings)} houses")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
