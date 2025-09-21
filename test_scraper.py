#!/usr/bin/env python3
"""
Test script for the house listing scraper
Run this to test the scraper functionality before setting up daily execution
"""

import os
import sys
from house_scraper import HouseListingScraper
from config import ZIP_CODES, FILTERS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_scraper():
    """Test the scraper with a single zip code"""
    print("🏠 Testing House Listing Scraper")
    print("=" * 50)
    
    # Display current configuration
    print(f"Searching in zip codes: {ZIP_CODES}")
    print(f"Price range: ${FILTERS['min_price']:,} - ${FILTERS['max_price']:,}")
    print(f"Year built: {FILTERS['min_year_built']} - {FILTERS['max_year_built']}")
    print(f"Property type: {FILTERS['property_type']}")
    print(f"Minimum bedrooms: {FILTERS['bedrooms']}")
    print(f"Minimum bathrooms: {FILTERS['bathrooms']}")
    print()
    
    # Check email configuration
    email_password = os.getenv('EMAIL_PASSWORD')
    if email_password:
        print("✅ Email configuration found")
    else:
        print("⚠️  EMAIL_PASSWORD not set - email notifications will be skipped")
        print("   Set EMAIL_PASSWORD environment variable to enable email notifications")
    print()
    
    # Initialize scraper
    print("Initializing scraper...")
    scraper = HouseListingScraper()
    
    try:
        # Test with first zip code only
        test_zip = ZIP_CODES[0] if ZIP_CODES else "10001"
        print(f"Testing with zip code: {test_zip}")
        print("This may take a few minutes...")
        print()
        
        # Scrape listings
        scraper.scrape_all_zip_codes()
        
        # Display results
        print(f"Found {len(scraper.listings)} matching houses")
        print()
        
        if scraper.listings:
            print("Sample listings:")
            for i, listing in enumerate(scraper.listings[:3], 1):  # Show first 3
                print(f"{i}. {listing.get('address', 'N/A')}")
                print(f"   Price: ${listing.get('price', 'N/A'):,}")
                print(f"   Details: {listing.get('bedrooms', 'N/A')} bed, {listing.get('bathrooms', 'N/A')} bath, {listing.get('sqft', 'N/A'):,} sqft")
                print(f"   Year: {listing.get('year_built', 'N/A')}")
                print(f"   Source: {listing.get('source', 'N/A')}")
                print()
        
        # Test email functionality
        if email_password:
            if scraper.listings:
                print("Testing email notification...")
                scraper.send_email_notification()
                print("✅ Email sent successfully!")
            else:
                print("⚠️  No listings found to send via email")
                print("   Run the email test separately: python test_email.py")
        else:
            print("⚠️  Skipping email test (no EMAIL_PASSWORD set)")
            print("   Set EMAIL_PASSWORD and run: python test_email.py")
        
        # Save to CSV
        scraper.save_to_csv("test_listings.csv")
        print("✅ Results saved to test_listings.csv")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        scraper.close()
    
    print()
    print("✅ Test completed successfully!")
    print("You can now set up daily execution using one of the methods in SETUP_GUIDE.md")
    return True

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)


