#!/usr/bin/env python3
"""
APISCRAPY Real Estate Scraper - Uses APISCRAPY API to get real property listings
"""

import requests
import json
import csv
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import time
import random
from config import ZIP_CODES, FILTERS, EMAIL_CONFIG
from house_scraper import HouseListingScraper

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

class APIScrapyScraper:
    """APISCRAPY scraper for real estate listings"""
    
    def __init__(self):
        self.api_key = os.getenv('APISCRAPY_API_KEY')
        self.base_url = 'https://api.apiscrapy.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.listings = []
        
        if not self.api_key:
            raise ValueError("APISCRAPY_API_KEY not found in environment variables")
    
    def search_properties_by_zip(self, zip_code):
        """Search for properties in a zip code"""
        logging.info(f"Searching properties in zip code {zip_code}")
        
        try:
            # APISCRAPY endpoint for property search
            url = f"{self.base_url}/real-estate/search"
            
            # Parameters for the search
            params = {
                'zipcode': zip_code,
                'min_price': FILTERS['min_price'],
                'max_price': FILTERS['max_price'],
                'min_bedrooms': 3,
                'min_bathrooms': 2,
                'min_sqft': FILTERS['min_sqft'],
                'property_type': 'house',
                'limit': 50
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Found {len(data.get('results', []))} properties in {zip_code}")
                return self._format_listings(data.get('results', []), zip_code)
            else:
                logging.warning(f"APISCRAPY returned status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logging.error(f"Error searching properties in {zip_code}: {e}")
            return []
    
    def search_properties_by_city(self, city, state):
        """Search for properties by city and state"""
        logging.info(f"Searching properties in {city}, {state}")
        
        try:
            url = f"{self.base_url}/real-estate/search"
            params = {
                'city': city,
                'state': state,
                'min_price': FILTERS['min_price'],
                'max_price': FILTERS['max_price'],
                'min_bedrooms': 3,
                'min_bathrooms': 2,
                'min_sqft': FILTERS['min_sqft'],
                'property_type': 'house',
                'limit': 100
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Found {len(data.get('results', []))} properties in {city}, {state}")
                return self._format_listings(data.get('results', []), '75024')  # Default to Plano
            else:
                logging.warning(f"APISCRAPY city search returned status {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error searching properties in {city}, {state}: {e}")
            return []
    
    def _format_listings(self, data, zip_code):
        """Format listings from API response"""
        listings = []
        
        for item in data:
            try:
                listing = {
                    'address': f"{item.get('address', 'N/A')}, {item.get('city', 'Plano')}, {item.get('state', 'TX')} {item.get('zipCode', zip_code)}",
                    'price': item.get('price', 0),
                    'bedrooms': item.get('bedrooms', 0),
                    'bathrooms': item.get('bathrooms', 0),
                    'sqft': item.get('squareFootage', item.get('sqft', 0)),
                    'year_built': item.get('yearBuilt', 0),
                    'home_type': 'house',
                    'url': item.get('url', item.get('listingUrl', 'N/A')),
                    'zestimate': item.get('zestimate', item.get('estimatedValue', 0)),
                    'zip_code': zip_code,
                    'source': 'APISCRAPY'
                }
                
                if self._matches_filters(listing):
                    listings.append(listing)
                    
            except Exception as e:
                logging.error(f"Error formatting listing: {e}")
                continue
        
        return listings
    
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
            if sqft > 0 and sqft < FILTERS['min_sqft']:
                return False
            
            # Property type filter
            home_type = listing.get('home_type', '').lower()
            if any(excluded in home_type for excluded in ['townhouse', 'townhome', 'condo', 'apartment']):
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking filters: {e}")
            return False
    
    def scrape_all_zip_codes(self):
        """Scrape all configured zip codes"""
        logging.info(f"Starting APISCRAPY scraping for {len(ZIP_CODES)} zip codes")
        
        all_listings = []
        
        for zip_code in ZIP_CODES:
            try:
                # Try zip code search first
                listings = self.search_properties_by_zip(zip_code)
                
                # If no results, try city search
                if not listings:
                    listings = self.search_properties_by_city('Plano', 'TX')
                
                all_listings.extend(listings)
                logging.info(f"Found {len(listings)} listings in {zip_code}")
                
                # Rate limiting - wait between zip codes
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logging.error(f"Error scraping zip {zip_code}: {e}")
                continue
        
        self.listings = all_listings
        logging.info(f"Total listings found: {len(all_listings)}")
        return all_listings
    
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

def main():
    """Main function to run the scraper"""
    try:
        # Initialize scraper
        scraper = APIScrapyScraper()
        
        # Test the API first
        logging.info("Testing APISCRAPY...")
        test_listings = scraper.search_properties_by_zip('75024')
        
        if test_listings:
            logging.info("✅ APISCRAPY is working!")
        else:
            logging.warning("⚠️ No test data found - check API key and filters")
        
        # Scrape all zip codes
        listings = scraper.scrape_all_zip_codes()
        
        if not listings:
            logging.warning("No listings found - check API key and filters")
            return
        
        # Save to CSV
        csv_file = scraper.save_to_csv()
        
        # Send email notification
        email_scraper = HouseListingScraper()
        email_scraper.listings = listings
        email_scraper.send_email_notification()
        
        logging.info("APISCRAPY scraping completed successfully!")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
