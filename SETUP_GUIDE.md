# House Listing Scraper - Setup Guide

## Overview
This scraper searches for houses in your specified zip codes with the following criteria:
- **Price Range:** $200,000 - $405,000
- **Year Built:** 1980 - 2020
- **Property Type:** Houses only (excludes townhomes and condos)
- **Minimum:** 2 bedrooms, 1 bathroom

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Email Notifications
1. Copy the example environment file:
   ```bash
   cp env_example.txt .env
   ```

2. Edit `.env` and add your Gmail App Password:
   ```
   EMAIL_PASSWORD=your_16_character_app_password
   ```

3. **Get Gmail App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Factor Authentication if not already enabled
   - Go to "App passwords" section
   - Generate a new app password for "Mail"
   - Use this 16-character password in your `.env` file

### 3. Configure Zip Codes
Edit `config.py` and update the `ZIP_CODES` list with your desired locations:
```python
ZIP_CODES = [
    "10001",  # Manhattan, NY
    "90210",  # Beverly Hills, CA
    # Add your zip codes here
]
```

### 4. Test the Scraper
```bash
python house_scraper.py
```

## Free Daily Execution Options

### Option 1: GitHub Actions (Recommended - 100% Free)
1. Create a GitHub repository
2. Add this workflow file at `.github/workflows/daily-scraper.yml`:

```yaml
name: Daily House Scraper

on:
  schedule:
    - cron: '0 8 * * *'  # Runs daily at 8:00 AM UTC
  workflow_dispatch:  # Allows manual runs

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        sudo apt-get update
        sudo apt-get install -y chromium-browser
    
    - name: Run scraper
      env:
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
      run: |
        python house_scraper.py
        python -c "
        from house_scraper import HouseListingScraper
        scraper = HouseListingScraper()
        scraper.scrape_all_zip_codes()
        scraper.send_email_notification()
        scraper.close()
        "
```

3. Add your email password as a GitHub Secret:
   - Go to repository Settings > Secrets and variables > Actions
   - Add new secret: `EMAIL_PASSWORD` with your Gmail app password

### Option 2: Heroku Scheduler (Free Tier Available)
1. Deploy to Heroku
2. Add Heroku Scheduler addon
3. Schedule daily job: `python house_scraper.py`

### Option 3: PythonAnywhere (Free Tier Available)
1. Upload your code to PythonAnywhere
2. Set up a daily task in the Tasks tab
3. Run: `python3 /home/yourusername/house-listing-scraper/house_scraper.py`

### Option 4: Local Computer with Cron (macOS/Linux)
1. Make the script executable:
   ```bash
   chmod +x run_daily.sh
   ```

2. Add to crontab:
   ```bash
   crontab -e
   ```

3. Add this line to run daily at 8 AM:
   ```
   0 8 * * * /Users/abdulloomonullaev/house-listing-scraper/run_daily.sh
   ```

### Option 5: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 8:00 AM
4. Set action to start program: `python.exe`
5. Add arguments: `C:\path\to\house_scraper.py`

## Email Notifications
The scraper will send you a beautifully formatted HTML email with:
- List of all matching houses
- Price, address, bedrooms, bathrooms, square footage
- Year built and source website
- Direct links to each listing
- Summary of search criteria

## Troubleshooting

### Common Issues:
1. **Chrome/Chromium not found:** Install Chrome or Chromium browser
2. **Email not sending:** Check your Gmail App Password
3. **No listings found:** Verify zip codes and check if websites are accessible
4. **Rate limiting:** Increase `REQUEST_DELAY` in config.py

### Logs:
- Check `scraper.log` for detailed execution logs
- Check `daily_run.log` for cron job logs

## Customization

### Modify Search Criteria:
Edit `config.py` to change:
- Price ranges
- Year built ranges
- Minimum bedrooms/bathrooms
- Zip codes to search

### Change Email Schedule:
Edit `SCHEDULE_TIME` in `config.py` (format: "HH:MM")

## Security Notes
- Never commit your `.env` file to version control
- Use App Passwords, not your regular email password
- Consider using environment variables for sensitive data

## Support
If you encounter issues:
1. Check the logs first
2. Verify your email configuration
3. Test with a single zip code first
4. Ensure all dependencies are installed correctly


