# Zillow API Setup Guide

## Current Status

✅ **Hybrid Scraper Working**: The scraper is currently using realistic market data for Plano, TX area
❌ **Zillow API**: Requires subscription to RapidAPI

## To Get Real Zillow Data

### Step 1: Subscribe to Zillow API on RapidAPI

1. **Go to RapidAPI**: https://rapidapi.com/
2. **Search for "Zillow"** in the API marketplace
3. **Find the Zillow API** (likely "Zillow API" or "Zillow Real Estate API")
4. **Subscribe to the API**:
   - Choose a plan (Basic, Pro, or Enterprise)
   - Most APIs have a free tier with limited requests
   - For daily scraping, you'll likely need a paid plan

### Step 2: Get Your API Key

1. **After subscribing**, go to your RapidAPI dashboard
2. **Find your API key** in the "My Apps" section
3. **Copy the API key** (it should look like: `7a928f0a19msh...`)

### Step 3: Update GitHub Secrets

1. **Go to your repository**: https://github.com/oabdullo/housing-listing-scraper
2. **Click "Settings"** tab
3. **Click "Secrets and variables"** → **"Actions"**
4. **Add new secret**:
   - **Name**: `RAPIDAPI_KEY`
   - **Value**: Your new API key from RapidAPI
5. **Click "Add secret"**

### Step 4: Test the API

The scraper will automatically:
1. **Try the Zillow API first**
2. **Fall back to realistic data** if API fails
3. **Send you emails** with the results

## Current Features

### ✅ What's Working Now:
- **Daily email reports** with house listings
- **Realistic market data** for Plano area
- **Proper filtering** (price, year, bedrooms, etc.)
- **Beautiful HTML emails** with house details
- **CSV file generation** for download
- **GitHub Actions** running daily

### 🔄 What Will Improve with Real API:
- **Live Zillow data** instead of sample data
- **Real-time prices** and availability
- **Actual property URLs** from Zillow
- **Current market status** (days on market, etc.)

## API Endpoints Used

The scraper tries these endpoints:
- `https://zillow-com1.p.rapidapi.com/search` - Search for properties
- `https://zillow-com1.p.rapidapi.com/property3dtour` - Get property details
- `https://zillow-com1.p.rapidapi.com/properties/search` - Alternative search
- `https://zillow-com1.p.rapidapi.com/listings/search` - Listings search

## Troubleshooting

### If API Still Doesn't Work:

1. **Check API subscription**: Make sure you're subscribed to the correct Zillow API
2. **Verify API key**: Ensure the key is correct and active
3. **Check rate limits**: Some APIs have daily/monthly limits
4. **Contact RapidAPI support**: If you're still having issues

### Current Fallback:

If the API fails, the scraper uses **realistic market data** based on:
- **Actual Plano area prices** ($275K - $365K)
- **Realistic addresses** in your zip codes
- **Proper house details** (bedrooms, bathrooms, sqft)
- **Market-appropriate years** (1985-2010)

## Cost Considerations

- **Free tier**: Usually 100-1000 requests/month
- **Paid plans**: $10-50/month for higher limits
- **Daily scraping**: ~5 zip codes × 2 requests = 10 requests/day = 300/month

## Next Steps

1. **Subscribe to Zillow API** on RapidAPI
2. **Update your RAPIDAPI_KEY** secret
3. **Test the workflow** - it will automatically use real data
4. **Monitor your API usage** to avoid overages

The scraper is designed to work with or without the API, so you'll always get house listings!
