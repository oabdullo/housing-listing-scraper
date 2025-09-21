# GitHub Actions Setup Guide

## ✅ Code Successfully Pushed!

Your Zillow56 scraper code has been pushed to GitHub and is ready for daily execution at 8 AM.

## 🔐 Required GitHub Secrets Setup

To make the scraper work, you need to add these secrets to your GitHub repository:

### 1. Go to Your Repository Settings
1. Navigate to: https://github.com/oabdullo/housing-listing-scraper
2. Click on **Settings** tab
3. Click on **Secrets and variables** → **Actions**

### 2. Add Required Secrets

Click **"New repository secret"** for each of these:

#### Secret 1: EMAIL_PASSWORD
- **Name**: `EMAIL_PASSWORD`
- **Value**: Your Gmail app password (the one you set in your .env file)

#### Secret 2: RAPIDAPI_KEY
- **Name**: `RAPIDAPI_KEY`
- **Value**: `7a928f0a19msh440eb1f91b9aa58p1d2761jsnf53cb3da03b3`

### 3. Verify Secrets
After adding both secrets, you should see:
- ✅ EMAIL_PASSWORD
- ✅ RAPIDAPI_KEY

## ⏰ Schedule Configuration

The workflow is configured to run:
- **Daily at 8:00 AM UTC** (which is 3:00 AM EST / 2:00 AM CST)
- **Manual trigger** available from GitHub Actions tab

### To Change Time Zone:
If you want it to run at 8 AM your local time, update the cron schedule in `.github/workflows/daily-scraper.yml`:

```yaml
schedule:
  - cron: '0 13 * * *'  # 8 AM EST (UTC-5)
  - cron: '0 14 * * *'  # 8 AM CST (UTC-6)
  - cron: '0 15 * * *'  # 8 AM MST (UTC-7)
  - cron: '0 16 * * *'  # 8 AM PST (UTC-8)
```

## 🚀 Testing the Workflow

### Manual Test:
1. Go to **Actions** tab in your repository
2. Click on **Daily House Scraper**
3. Click **"Run workflow"** button
4. Click **"Run workflow"** to start

### Check Results:
- The workflow will run for about 2-3 minutes
- Results will be uploaded as artifacts
- Check the **Actions** tab for logs and results

## 📊 What Happens Daily:

1. **8:00 AM UTC**: GitHub Actions triggers
2. **API Call**: Single request to Zillow56 API
3. **Data Processing**: Filters houses matching your criteria
4. **CSV Export**: Saves results to CSV file
5. **Email Notification**: Sends email to omoabdullo@gmail.com
6. **Artifact Upload**: Saves results for 30 days

## 📈 Expected Results:

Based on your test, you should get:
- **6-10 houses** per day in Plano area
- **Price range**: $200K - $405K
- **Bedrooms**: 2+ bedrooms
- **Bathrooms**: 1+ bathrooms
- **Square feet**: 1,400+ sqft
- **API usage**: 1 call per day (29 remaining this month)

## 🔧 Troubleshooting:

### If workflow fails:
1. Check **Actions** tab for error logs
2. Verify secrets are set correctly
3. Check if API key has remaining calls
4. Verify email credentials

### If no houses found:
- This is normal - not every day will have new listings
- The scraper will still run and send an email
- Check the logs to see what happened

## 📧 Email Notifications:

You'll receive daily emails with:
- List of houses found
- Price, address, bedrooms, bathrooms, sqft
- Direct links to Zillow listings
- CSV file attachment

## 🎯 Success Indicators:

✅ **Workflow runs successfully**  
✅ **CSV file generated**  
✅ **Email sent to omoabdullo@gmail.com**  
✅ **API calls remaining: 29**  

Your scraper is now fully automated and will run daily at 8 AM! 🏠✨
