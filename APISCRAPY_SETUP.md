# APISCRAPY Setup Guide

## Why APISCRAPY?

APISCRAPY is the **best free option** for getting real estate data because:
- ✅ **Free tier available** - No cost for basic usage
- ✅ **Real data** - Scrapes from Zillow, Realtor.com, Trulia
- ✅ **No blocking** - Handles anti-bot measures
- ✅ **Reliable** - Designed for this purpose
- ✅ **Easy setup** - Just need an API key

## Step 1: Get APISCRAPY API Key

1. **Visit APISCRAPY**: Go to [https://apiscrapy.com/real-estate-api/](https://apiscrapy.com/real-estate-api/)
2. **Sign up**: Create a free account
3. **Get API Key**: Find your API key in the dashboard
4. **Copy the key**: It will look like `apiscrapy_xxxxxxxxxxxxxxxx`

## Step 2: Add API Key to Environment

1. **Open your `.env` file**:
   ```bash
   nano .env
   ```

2. **Add the API key**:
   ```
   APISCRAPY_API_KEY=apiscrapy_your_actual_api_key_here
   ```

3. **Save the file** (Ctrl+X, then Y, then Enter)

## Step 3: Test the Setup

Run the test script to verify everything works:

```bash
python3 apiscrapy_scraper.py
```

## Step 4: Update GitHub Actions

1. **Go to your GitHub repository**
2. **Click Settings** → **Secrets and variables** → **Actions**
3. **Add new secret**:
   - Name: `APISCRAPY_API_KEY`
   - Value: `apiscrapy_your_actual_api_key_here`

## Step 5: Update Scheduler

The scheduler will automatically use APISCRAPY once you add the API key.

## API Limits

- **Free Tier**: 1,000 requests/month
- **Rate Limit**: 10 requests/minute
- **Data**: Real-time from multiple sites

## Troubleshooting

### "API key not found" error
- Make sure you've added `APISCRAPY_API_KEY` to your `.env` file
- Check that the API key is correct (starts with `apiscrapy_`)

### "No listings found" error
- Verify your API key is valid
- Check if you've exceeded your monthly limit
- Try a different zip code to test

### Rate limit errors
- The scraper includes built-in delays
- If you hit limits, wait a few minutes and try again

## Why This is Better Than Web Scraping

| Method | Reliability | Maintenance | Cost | Data Quality |
|--------|-------------|-------------|------|--------------|
| Web Scraping | Low | High | $0 | Medium |
| APISCRAPY | High | Low | $0 | High |
| Hybrid (Current) | Medium | Low | $0 | Low |

## Next Steps

1. **Get your APISCRAPY API key**
2. **Add it to your `.env` file**
3. **Test the scraper**: `python3 apiscrapy_scraper.py`
4. **Add the key to GitHub Secrets**
5. **The scraper will run daily automatically!**

## Support

- **APISCRAPY Support**: Check their website for documentation
- **API Documentation**: Available after signup
- **Free Tier**: Should be plenty for daily scraping

This will give you **real, live data** instead of the mocked hybrid data! 🎉
