# House Listing Scraper

A daily automated house listing scraper that searches for houses in the Plano, TX area using the Zillow56 API via RapidAPI. The scraper runs daily at 8 AM and sends email notifications with real house listings matching your criteria.

## Features

- 🏠 **Real Zillow Data**: Uses Zillow56 API for authentic house listings
- 📧 **Email Notifications**: Daily emails with house details and links
- ⏰ **Automated Scheduling**: Runs daily at 8 AM via GitHub Actions
- 💰 **Cost Efficient**: Uses only 1 API call per day (30 calls/month limit)
- 🎯 **Filtered Results**: Only shows houses matching your specific criteria

## Search Criteria

- **Location**: Plano, TX area (zip codes: 75024, 75023, 75074, 75093, 75056)
- **Price Range**: $200,000 - $405,000
- **Property Type**: Houses only (no townhomes, condos, apartments)
- **Bedrooms**: 2+ bedrooms
- **Bathrooms**: 1+ bathrooms
- **Square Feet**: 1,400+ sqft
- **Year Built**: 1980-2020

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/oabdullo/housing-listing-scraper.git
cd housing-listing-scraper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file with your credentials:
```bash
EMAIL_PASSWORD=your_gmail_app_password
RAPIDAPI_KEY=your_rapidapi_key
```

### 4. Test the Scraper
```bash
python3 test_zillow56.py
```

### 5. Run the Scraper
```bash
python3 zillow56_scraper.py
```

## GitHub Actions Setup

The scraper is configured to run daily at 8 AM UTC via GitHub Actions.

### Required GitHub Secrets
Add these secrets to your repository settings:

1. **EMAIL_PASSWORD**: Your Gmail app password
2. **RAPIDAPI_KEY**: Your RapidAPI key for Zillow56

### Manual Trigger
You can manually trigger the workflow from the GitHub Actions tab.

## File Structure

```
house-listing-scraper/
├── zillow56_scraper.py      # Main scraper (Zillow56 API)
├── test_zillow56.py         # Test script
├── scheduler.py             # Daily scheduler
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .github/workflows/       # GitHub Actions workflow
└── README.md               # This file
```

## Configuration

Edit `config.py` to customize your search criteria:

```python
# Search filters
FILTERS = {
    "min_price": 200000,      # Minimum price
    "max_price": 405000,      # Maximum price
    "min_year_built": 1980,   # Minimum year built
    "max_year_built": 2020,   # Maximum year built
    "min_sqft": 1400,         # Minimum square footage
    "max_sqft": 5000,         # Maximum square footage
    "bedrooms": 2,            # Minimum bedrooms
    "bathrooms": 1,           # Minimum bathrooms
    "property_type": "house", # Property type
}

# Email settings
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "omoabdullo@gmail.com",
    "recipient_email": "omoabdullo@gmail.com",
}
```

## API Usage

- **Provider**: Zillow56 via RapidAPI
- **Daily Usage**: 1 API call per day
- **Monthly Limit**: 30 calls (perfect for daily use)
- **Cost**: Free tier available

## Email Notifications

Daily emails include:
- Number of houses found
- House details (price, address, bedrooms, bathrooms, sqft)
- Direct links to Zillow listings
- Search criteria summary

## Troubleshooting

### No Email Received
1. Check your spam folder
2. Verify EMAIL_PASSWORD in GitHub Secrets
3. Check GitHub Actions logs for errors

### No Houses Found
- This is normal - not every day has new listings
- Check the logs to see what happened
- Verify your search criteria in config.py

### API Errors
- Check if you have remaining API calls
- Verify RAPIDAPI_KEY in GitHub Secrets
- Check the GitHub Actions logs

## Support

For issues or questions:
1. Check the GitHub Actions logs
2. Verify your environment variables
3. Test locally with `python3 test_zillow56.py`

## License

This project is for personal use only. Please respect Zillow's terms of service and API usage limits.