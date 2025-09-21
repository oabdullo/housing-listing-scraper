#!/usr/bin/env python3
"""
GitHub Actions runner for house listing scraper
This script is optimized for running in GitHub Actions environment
"""

import os
import sys
import time
import logging
from datetime import datetime
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

def create_sample_listings():
    """Create sample house listings for testing"""
    # This simulates what the scraper would find
    sample_listings = [
        {
            'source': 'Zillow',
            'zip_code': '75024',
            'scraped_at': datetime.now().isoformat(),
            'price': 350000,
            'address': '123 Main St, Plano, TX 75024',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1800,
            'year_built': 1995,
            'url': 'https://www.zillow.com/homedetails/123-Main-St-Plano-TX-75024/123456789_zpid/',
            'property_type': 'house'
        },
        {
            'source': 'Realtor.com',
            'zip_code': '75023',
            'scraped_at': datetime.now().isoformat(),
            'price': 280000,
            'address': '456 Oak Ave, Frisco, TX 75023',
            'bedrooms': 4,
            'bathrooms': 3,
            'sqft': 2200,
            'year_built': 2005,
            'url': 'https://www.realtor.com/realestateandhomes-detail/456-Oak-Ave-Frisco-TX-75023_M12345-12345',
            'property_type': 'house'
        },
        {
            'source': 'Zillow',
            'zip_code': '75074',
            'scraped_at': datetime.now().isoformat(),
            'price': 320000,
            'address': '789 Pine St, Allen, TX 75074',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1600,
            'year_built': 1985,
            'url': 'https://www.zillow.com/homedetails/789-Pine-St-Allen-TX-75074/987654321_zpid/',
            'property_type': 'house'
        },
        {
            'source': 'Realtor.com',
            'zip_code': '75093',
            'scraped_at': datetime.now().isoformat(),
            'price': 295000,
            'address': '321 Elm Dr, Plano, TX 75093',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1750,
            'year_built': 1990,
            'url': 'https://www.realtor.com/realestateandhomes-detail/321-Elm-Dr-Plano-TX-75093_M67890-67890',
            'property_type': 'house'
        },
        {
            'source': 'Zillow',
            'zip_code': '75056',
            'scraped_at': datetime.now().isoformat(),
            'price': 380000,
            'address': '654 Maple Ln, Frisco, TX 75056',
            'bedrooms': 4,
            'bathrooms': 3,
            'sqft': 2400,
            'year_built': 2010,
            'url': 'https://www.zillow.com/homedetails/654-Maple-Ln-Frisco-TX-75056/111222333_zpid/',
            'property_type': 'house'
        }
    ]
    
    # Filter listings based on criteria
    filtered_listings = []
    for listing in sample_listings:
        if matches_filters(listing):
            filtered_listings.append(listing)
    
    return filtered_listings

def matches_filters(listing):
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

def create_email_html(listings):
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
            <p><strong>Total Houses Found:</strong> {len(listings)}</p>
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
    
    for i, listing in enumerate(listings, 1):
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

def send_email_notification(listings):
    """Send email notification with house listings"""
    if not listings:
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
        msg['Subject'] = f"Daily House Listings - {len(listings)} houses found"
        
        # Create HTML body with house listings
        html_body = create_email_html(listings)
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], email_password)
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        logger.info(f"Email notification sent successfully with {len(listings)} listings")
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")

def save_to_csv(listings, filename="house_listings.csv"):
    """Save listings to CSV file"""
    if not listings:
        logger.warning("No listings to save")
        return
    
    import pandas as pd
    df = pd.DataFrame(listings)
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(listings)} listings to {filename}")

def main():
    """Main function for GitHub Actions"""
    logger.info("Starting GitHub Actions house listing scraper...")
    
    try:
        # Get sample listings (in a real scenario, this would be actual scraping)
        logger.info(f"Searching in zip codes: {ZIP_CODES}")
        logger.info(f"Price range: ${FILTERS['min_price']:,} - ${FILTERS['max_price']:,}")
        logger.info(f"Year built: {FILTERS['min_year_built']} - {FILTERS['max_year_built']}")
        
        # Create sample listings
        listings = create_sample_listings()
        logger.info(f"Found {len(listings)} matching houses")
        
        if listings:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"house_listings_{timestamp}.csv"
            save_to_csv(listings, filename)
            
            # Send email notification
            send_email_notification(listings)
            
            logger.info("GitHub Actions run completed successfully!")
        else:
            logger.info("No matching houses found")
            
    except Exception as e:
        logger.error(f"Error during GitHub Actions run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
