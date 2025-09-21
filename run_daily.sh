#!/bin/bash

# Daily House Listing Scraper Runner
# This script runs the scraper and handles logging

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up logging
LOG_FILE="daily_run.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting daily house listing scrape..." >> "$LOG_FILE"

# Run the scraper
python3 scheduler.py --once >> "$LOG_FILE" 2>&1

# Check if the run was successful
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Daily scrape completed successfully" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] Daily scrape failed" >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] Daily run finished" >> "$LOG_FILE"
