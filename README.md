# 🏠 Daily House Listing Scraper

Automatically scrapes house listings from Zillow and Realtor.com and sends daily email reports with matching properties.

## Features

- **Daily Email Reports**: Beautiful HTML emails with house details, prices, and direct links
- **Customizable Filters**: Price range, year built, property type, bedrooms, bathrooms
- **Multiple Sources**: Scrapes from Zillow and Realtor.com
- **Automated Execution**: Runs daily via GitHub Actions
- **Texas Focus**: Currently configured for Dallas-Fort Worth area zip codes

## Current Search Criteria

- **Price Range**: $200,000 - $405,000
- **Year Built**: 1980 - 2020
- **Property Type**: Houses only (excludes townhomes and condos)
- **Minimum**: 2 bedrooms, 1 bathroom
- **Minimum Square Footage**: 1,400 sqft

## Zip Codes Searched

- 75024 (Plano, TX)
- 75023 (Frisco, TX)
- 75074 (Allen, TX)
- 75093 (Plano, TX)
- 75056 (Frisco, TX)

## Setup

1. **Fork this repository**
2. **Set up email notifications**:
   - Go to repository Settings > Secrets and variables > Actions
   - Add new secret: `EMAIL_PASSWORD`
   - Use your Gmail App Password (16 characters)

3. **Customize search criteria** (optional):
   - Edit `config.py` to change zip codes, price ranges, etc.

4. **Enable GitHub Actions**:
   - Go to Actions tab in your repository
   - Enable workflows if prompted

## How It Works

1. **Daily Execution**: Runs every day at 8:00 AM UTC via GitHub Actions
2. **Web Scraping**: Uses Selenium to scrape Zillow and Realtor.com
3. **Filtering**: Applies your custom criteria to find matching houses
4. **Email Report**: Sends HTML email with all matching properties
5. **Data Storage**: Saves results as CSV files (available for 30 days)

## Email Reports Include

- Property address and price
- Bedrooms, bathrooms, square footage
- Year built and source website
- Direct links to each listing
- Search criteria summary

## Manual Testing

To test the scraper manually:

```bash
# Test email functionality only
python3 simple_email_test.py

# Test full scraper (requires Chrome)
python3 test_scraper.py
```

## Customization

### Change Zip Codes
Edit `config.py`:
```python
ZIP_CODES = [
    "your_zip_code_1",
    "your_zip_code_2",
    # Add more zip codes
]
```

### Modify Search Criteria
Edit `config.py`:
```python
FILTERS = {
    "min_price": 200000,
    "max_price": 405000,
    "min_year_built": 1980,
    "max_year_built": 2020,
    # ... other filters
}
```

### Change Email Schedule
Edit `.github/workflows/daily-scraper.yml`:
```yaml
schedule:
  - cron: '0 8 * * *'  # Change time (UTC)
```

## Troubleshooting

- **No emails received**: Check spam folder and verify EMAIL_PASSWORD secret
- **No listings found**: Verify zip codes and check if websites are accessible
- **Workflow failures**: Check Actions tab for error logs

## Security

- Email passwords are stored as GitHub Secrets
- No sensitive data is committed to the repository
- Uses Gmail App Passwords for secure authentication

## License

MIT License - feel free to modify and use for your own house hunting!