#!/usr/bin/env python3
"""
Simple email test with sample house data
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from config import EMAIL_CONFIG, FILTERS

# Load environment variables
load_dotenv()

def create_sample_email_html():
    """Create HTML email with sample house listings"""
    sample_listings = [
        {
            'price': 350000,
            'address': '123 Main St, Plano, TX 75024',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1800,
            'year_built': 1995,
            'url': 'https://www.zillow.com/homedetails/123-Main-St-Plano-TX-75024/123456789_zpid/',
            'source': 'Zillow'
        },
        {
            'price': 280000,
            'address': '456 Oak Ave, Frisco, TX 75023',
            'bedrooms': 4,
            'bathrooms': 3,
            'sqft': 2200,
            'year_built': 2005,
            'url': 'https://www.realtor.com/realestateandhomes-detail/456-Oak-Ave-Frisco-TX-75023_M12345-12345',
            'source': 'Realtor.com'
        },
        {
            'price': 320000,
            'address': '789 Pine St, Allen, TX 75074',
            'bedrooms': 3,
            'bathrooms': 2,
            'sqft': 1600,
            'year_built': 1985,
            'url': 'https://www.zillow.com/homedetails/789-Pine-St-Allen-TX-75074/987654321_zpid/',
            'source': 'Zillow'
        }
    ]
    
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
            <p><strong>Total Houses Found:</strong> {len(sample_listings)}</p>
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
    
    for i, listing in enumerate(sample_listings, 1):
        price = f"${listing['price']:,}"
        address = listing['address']
        bedrooms = listing['bedrooms']
        bathrooms = listing['bathrooms']
        sqft = f"{listing['sqft']:,}"
        year_built = listing['year_built']
        url = listing['url']
        source = listing['source']
        
        html += f"""
        <div class="listing">
            <div class="price">{price}</div>
            <div class="address">{address}</div>
            <div class="details">
                <strong>Details:</strong> {bedrooms} bed, {bathrooms} bath, {sqft} sqft, Built: {year_built}
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

def test_sample_email():
    """Test email with sample house data"""
    print("📧 Testing Email with Sample House Data")
    print("=" * 50)
    
    # Check email password
    email_password = os.getenv('EMAIL_PASSWORD')
    if not email_password:
        print("❌ EMAIL_PASSWORD not found in .env file")
        return False
    
    print(f"✅ Email password found (length: {len(email_password)})")
    print(f"📤 Sender: {EMAIL_CONFIG['sender_email']}")
    print(f"📥 Recipient: {EMAIL_CONFIG['recipient_email']}")
    print()
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = "Test: Daily House Listings - 3 sample houses found"
        
        # Create HTML body
        html_body = create_sample_email_html()
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        print("🔄 Sending email...")
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], email_password)
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        print("✅ Sample email sent successfully!")
        print("Check your inbox for the house listings email with sample data.")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    success = test_sample_email()
    if success:
        print("\n🎉 Email functionality is working perfectly!")
        print("Your scraper is ready to send daily house listings.")
    else:
        print("\n❌ Email test failed. Check the error message above.")
