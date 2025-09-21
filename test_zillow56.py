#!/usr/bin/env python3
"""
Test Zillow56 API with your specific criteria
"""

import requests
import json
from dotenv import load_dotenv
import os
from config import FILTERS

# Load environment variables
load_dotenv()

def test_zillow56_api():
    """Test the Zillow56 API with your Plano search criteria"""
    
    api_key = os.getenv('RAPIDAPI_KEY')
    
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in .env file")
        return
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'zillow56.p.rapidapi.com'
    }
    
    url = 'https://zillow56.p.rapidapi.com/search'
    
    # Your exact search criteria from config.py
    params = {
        'location': 'Plano, TX',
        'home_type': 'Houses',
        'min_price': FILTERS['min_price'],
        'max_price': FILTERS['max_price'],
        'min_bedrooms': FILTERS['bedrooms'],
        'min_bathrooms': FILTERS['bathrooms'],
        'min_sqft': FILTERS['min_sqft'],
        'max_sqft': FILTERS['max_sqft'],
        'min_year_built': FILTERS['min_year_built'],
        'max_year_built': FILTERS['max_year_built'],
        'sort': 'newest',
        'limit': 10  # Small limit for testing
    }
    
    print("\n🔍 Testing Zillow56 API with your criteria...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Search Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            print(f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Try to extract listings
            results = []
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                elif 'listings' in data:
                    results = data['listings']
                elif 'properties' in data:
                    results = data['properties']
                elif 'homes' in data:
                    results = data['homes']
                elif 'data' in data:
                    results = data['data']
                else:
                    results = [data] if data else []
            elif isinstance(data, list):
                results = data
            
            print(f"\n📊 Found {len(results)} results")
            
            if results:
                print("\n🏠 Sample listings:")
                for i, listing in enumerate(results[:3], 1):  # Show first 3
                    print(f"\n  Listing {i}:")
                    print(f"    Address: {listing.get('address', 'N/A')}")
                    print(f"    Price: ${listing.get('price', 'N/A'):,}")
                    print(f"    Bedrooms: {listing.get('bedrooms', 'N/A')}")
                    print(f"    Bathrooms: {listing.get('bathrooms', 'N/A')}")
                    print(f"    Square Feet: {listing.get('livingArea', 'N/A')}")
                    print(f"    Year Built: {listing.get('yearBuilt', 'N/A')}")
                    print(f"    URL: {listing.get('url', 'N/A')}")
            else:
                print("⚠️ No listings found in response")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== Testing Zillow56 API with Your Plano Search Criteria ===")
    test_zillow56_api()
    print("\n=== Next Steps ===")
    print("1. If the test works, run: python zillow56_scraper.py")
    print("2. If it fails, check your RAPIDAPI_KEY in .env file")
    print("3. Make sure you have remaining API calls for this month")
