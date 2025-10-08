#!/usr/bin/env python3
"""
Test script for both house listing scrapers
Run this to test both Plano TX and Warwick NY scrapers
"""

import subprocess
import sys
import os
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_plano_scraper():
    """Test the Plano TX scraper"""
    logger.info("🧪 Testing Plano TX scraper...")
    
    try:
        # Switch to main branch
        subprocess.run(['git', 'checkout', 'main'], check=True)
        logger.info("✅ Switched to main branch")
        
        # Run the scraper
        result = subprocess.run([sys.executable, 'zillow56_scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Plano TX scraper completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ Plano TX scraper failed: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Plano TX scraper timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Plano TX scraper: {e}")
        return False

def test_warwick_scraper():
    """Test the Warwick NY scraper"""
    logger.info("🧪 Testing Warwick NY scraper...")
    
    try:
        # Switch to warwick-ny-scraper branch
        subprocess.run(['git', 'checkout', 'warwick-ny-scraper'], check=True)
        logger.info("✅ Switched to warwick-ny-scraper branch")
        
        # Run the scraper
        result = subprocess.run([sys.executable, 'zillow56_scraper.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Warwick NY scraper completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error(f"❌ Warwick NY scraper failed: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Warwick NY scraper timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Warwick NY scraper: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = ['RAPIDAPI_KEY', 'EMAIL_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables before running the test")
        return False
    else:
        logger.info("✅ All required environment variables are set")
        return True

def main():
    """Main test function"""
    logger.info("🚀 Starting scraper tests...")
    logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Test results
    plano_success = False
    warwick_success = False
    
    # Test Plano scraper
    try:
        plano_success = test_plano_scraper()
    except Exception as e:
        logger.error(f"❌ Unexpected error testing Plano scraper: {e}")
    
    # Wait a bit between tests
    time.sleep(5)
    
    # Test Warwick scraper
    try:
        warwick_success = test_warwick_scraper()
    except Exception as e:
        logger.error(f"❌ Unexpected error testing Warwick scraper: {e}")
    
    # Summary
    logger.info("=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Plano TX Scraper: {'✅ PASSED' if plano_success else '❌ FAILED'}")
    logger.info(f"Warwick NY Scraper: {'✅ PASSED' if warwick_success else '❌ FAILED'}")
    
    if plano_success and warwick_success:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
