#!/bin/bash

# Setup script for dual house listing scrapers
# This script sets up cron jobs for both Plano TX and Warwick NY scrapers

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "Setting up cron jobs for house listing scrapers..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create the cron job entries
CRON_ENTRY1="# Plano TX scraper - runs at 8:00 AM daily"
CRON_ENTRY2="0 8 * * * cd $SCRIPT_DIR && git checkout main && $PYTHON_PATH scheduler.py >> $SCRIPT_DIR/plano_scraper.log 2>&1"
CRON_ENTRY3=""
CRON_ENTRY4="# Warwick NY scraper - runs at 9:00 AM daily"
CRON_ENTRY5="0 9 * * * cd $SCRIPT_DIR && git checkout warwick-ny-scraper && $PYTHON_PATH warwick_scheduler.py >> $SCRIPT_DIR/warwick_scraper.log 2>&1"

# Create a temporary cron file
TEMP_CRON="/tmp/house_scraper_cron"

# Add the new cron jobs
{
    echo "$CRON_ENTRY1"
    echo "$CRON_ENTRY2"
    echo "$CRON_ENTRY3"
    echo "$CRON_ENTRY4"
    echo "$CRON_ENTRY5"
} > "$TEMP_CRON"

# Install the cron jobs
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "Cron jobs installed successfully!"
echo ""
echo "Current cron jobs:"
crontab -l
echo ""
echo "To test the scrapers manually:"
echo "  Plano TX: cd $SCRIPT_DIR && git checkout main && $PYTHON_PATH scheduler.py --once"
echo "  Warwick NY: cd $SCRIPT_DIR && git checkout warwick-ny-scraper && $PYTHON_PATH warwick_scheduler.py --once"
echo ""
echo "To view logs:"
echo "  Plano TX: tail -f $SCRIPT_DIR/plano_scraper.log"
echo "  Warwick NY: tail -f $SCRIPT_DIR/warwick_scraper.log"
