# Testing Guide for House Listing Scrapers

This guide covers how to test both the Plano TX and Warwick NY house listing scrapers.

## 🚀 Quick Start Testing

### Prerequisites
1. Ensure you have the required environment variables set:
   ```bash
   export RAPIDAPI_KEY="your_rapidapi_key_here"
   export EMAIL_PASSWORD="your_gmail_app_password_here"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🧪 Testing Individual Scrapers

### Test Plano TX Scraper
```bash
# Switch to main branch
git checkout main

# Run Plano scraper once
python scheduler.py --once

# Or run the scraper directly
python zillow56_scraper.py
```

### Test Warwick NY Scraper
```bash
# Switch to warwick-ny-scraper branch
git checkout warwick-ny-scraper

# Run Warwick scraper once
python warwick_scheduler.py --once

# Or run the scraper directly
python zillow56_scraper.py
```

## 📧 Email Testing

### Test Email Functionality
Both scrapers will send emails to their respective recipients:

- **Plano TX**: Sends to `omoabdullo@gmail.com`
- **Warwick NY**: Sends to both:
  - `Brett.davidson5@outlook.com`
  - `alexamariefini820@gmail.com`

### Email Test Mode
To test with only one recipient for Warwick scraper:
```python
# In zillow56_scraper.py or warwick_scheduler.py
scraper.send_email_notification(test_mode=True)  # Sends to Brett only
scraper.send_email_notification(test_mode=False) # Sends to both recipients
```

## 🔄 Testing Both Scrapers Together

### Option 1: Dual Scraper Manager
```bash
# Run both scrapers simultaneously
python run_dual_scrapers.py
```

### Option 2: Manual Parallel Testing
```bash
# Terminal 1 - Plano scraper
git checkout main
python scheduler.py

# Terminal 2 - Warwick scraper (in another terminal)
git checkout warwick-ny-scraper
python warwick_scheduler.py
```

## 📊 Monitoring and Logs

### View Logs
```bash
# Plano TX logs
tail -f plano_scraper.log

# Warwick NY logs
tail -f warwick_scraper.log

# Dual scraper logs
tail -f dual_scraper.log

# General scraper logs
tail -f scraper.log
```

### Check Results
```bash
# List generated CSV files
ls -la house_listings_*.csv
ls -la warwick_listings_*.csv
```

## 🕐 Cron Job Testing

### Set Up Cron Jobs
```bash
# Run the setup script
./setup_cron.sh

# Check installed cron jobs
crontab -l
```

### Test Cron Jobs
```bash
# Test Plano scraper at 8:00 AM
0 8 * * * cd /path/to/scraper && git checkout main && python scheduler.py

# Test Warwick scraper at 9:00 AM
0 9 * * * cd /path/to/scraper && git checkout warwick-ny-scraper && python warwick_scheduler.py
```

## 🐛 Debugging

### Common Issues

1. **API Key Issues**
   ```bash
   echo $RAPIDAPI_KEY  # Should show your API key
   ```

2. **Email Password Issues**
   ```bash
   echo $EMAIL_PASSWORD  # Should show your Gmail app password
   ```

3. **Branch Issues**
   ```bash
   git branch  # Check current branch
   git status  # Check for uncommitted changes
   ```

4. **Permission Issues**
   ```bash
   chmod +x setup_cron.sh
   ```

### Verbose Logging
Add debug logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 GitHub Actions Testing

### Manual Workflow Trigger
1. Go to your GitHub repository
2. Click on "Actions" tab
3. Select "Daily House Scraper" workflow
4. Click "Run workflow" button
5. Choose branch and click "Run workflow"

### Workflow Testing
The GitHub Actions workflow will:
1. Checkout the code
2. Set up Python environment
3. Install dependencies
4. Run the scraper
5. Upload results as artifacts

## 📈 Expected Results

### Plano TX Scraper
- Searches zip codes: 75024, 75023, 75074, 75093, 75056
- Sends to: omoabdullo@gmail.com
- Runs at: 8:00 AM daily

### Warwick NY Scraper
- Searches zip codes: 10990, 10918, 10921, 10924, 10925, 10950, 10958, 10969, 10987
- Sends to: Brett.davidson5@outlook.com, alexamariefini820@gmail.com
- Runs at: 9:00 AM daily

## 🔧 Configuration Testing

### Test Different Configurations
Edit `config.py` to test different:
- Price ranges
- Property types
- Square footage requirements
- Bedroom/bathroom requirements

### Test Different Zip Codes
Add or remove zip codes in the `ZIP_CODES` list in `config.py`

## 📝 Troubleshooting

### No Listings Found
1. Check if API key is valid
2. Verify zip codes are correct
3. Check if filters are too restrictive
4. Review API response in logs

### Email Not Sending
1. Verify EMAIL_PASSWORD is set
2. Check Gmail app password is correct
3. Ensure recipient emails are valid
4. Check SMTP settings

### Cron Jobs Not Running
1. Check if cron service is running
2. Verify cron job syntax
3. Check file paths are correct
4. Review cron logs: `grep CRON /var/log/syslog`
