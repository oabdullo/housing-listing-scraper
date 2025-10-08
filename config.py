"""
Configuration file for house listing scraper
Modify the values below to customize your search criteria
"""

# Zip codes to search (add your desired zip codes here)
ZIP_CODES = [
    "10990",  # Warwick, NY
]

# Search filters
FILTERS = {
    "min_price": 200000,      # Minimum price
    "max_price": 405000,      # Maximum price
    "min_year_built": 1980,   # Minimum year built
    "max_year_built": 2020,   # Maximum year built
    "min_sqft": 1300,         # Minimum square footage
    "max_sqft": 5000,         # Maximum square footage
    "bedrooms": 2,            # Minimum bedrooms
    "bathrooms": 1,           # Minimum bathrooms
    "property_type": ["house", "townhouse", "condo", "apartment"], # Property type (house, townhouse, condo, etc.)
}

# Job scheduling
SCHEDULE_TIME = "08:00"  # 8:00 AM daily

# Output settings
OUTPUT_FILE = "house_listings.csv"
LOG_FILE = "scraper.log"

# Web scraping settings
REQUEST_DELAY = 2  # Delay between requests (seconds)
MAX_RETRIES = 3    # Maximum retry attempts

# Email settings
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "omoabdullo@gmail.com",
    "recipient_emails": [
        "Brett.davidson5@outlook.com",
        "alexamariefini820@gmail.com"
    ],
    "test_recipient": "Brett.davidson5@outlook.com",  # For testing with one email
    "password": "",  # Set via environment variable EMAIL_PASSWORD
}
