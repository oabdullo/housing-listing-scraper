#!/usr/bin/env python3
"""
Test email functionality with sample house data
"""

import os
from dotenv import load_dotenv
from house_scraper import HouseListingScraper

# Load environment variables
load_dotenv()

def test_email_with_sample_data():
    """Test email with sample house data"""
    print("📧 Testing Email with Sample House Data")
    print("=" * 50)
    
    # Create a scraper instance
    scraper = HouseListingScraper()
    
    # Add some sample house data
    sample_listings = [
        {
            'source': 'Zillow',
            'zip_code': '75024',
            'scraped_at': '2024-09-21T15:48:00',
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
            'scraped_at': '2024-09-21T15:48:00',
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
            'scraped_at': '2024-09-21T15:48:00',
            'price': 320000,
            'address': '789 Pine St, Allen, TX 75074',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1600,
            'year_built': 1985,
            'url': 'https://www.zillow.com/homedetails/789-Pine-St-Allen-TX-75074/987654321_zpid/',
            'property_type': 'house'
        }
    ]
    
    # Add sample data to scraper
    scraper.listings = sample_listings
    
    print(f"📊 Sample data: {len(scraper.listings)} houses")
    print("📤 Sending email with sample house listings...")
    
    try:
        scraper.send_email_notification()
        print("✅ Email sent successfully!")
        print("Check your inbox for the house listings email.")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    success = test_email_with_sample_data()
    if success:
        print("\n🎉 Email functionality is working perfectly!")
        print("Your scraper is ready to send daily house listings.")
    else:
        print("\n❌ Email test failed. Check the error message above.")
