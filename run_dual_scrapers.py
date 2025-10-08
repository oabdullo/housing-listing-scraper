#!/usr/bin/env python3
"""
Dual scraper runner - runs both Plano TX and Warwick NY scrapers
This script manages both scrapers running in parallel
"""

import subprocess
import sys
import os
import time
import signal
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dual_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DualScraperManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def start_plano_scraper(self):
        """Start the Plano TX scraper"""
        try:
            # Switch to main branch for Plano scraper
            subprocess.run(['git', 'checkout', 'main'], check=True)
            
            # Start the Plano scheduler
            plano_process = subprocess.Popen([
                sys.executable, 'scheduler.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['plano'] = plano_process
            logger.info("Plano TX scraper started")
            
        except Exception as e:
            logger.error(f"Failed to start Plano scraper: {e}")
    
    def start_warwick_scraper(self):
        """Start the Warwick NY scraper"""
        try:
            # Switch to warwick-ny-scraper branch
            subprocess.run(['git', 'checkout', 'warwick-ny-scraper'], check=True)
            
            # Start the Warwick scheduler
            warwick_process = subprocess.Popen([
                sys.executable, 'warwick_scheduler.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['warwick'] = warwick_process
            logger.info("Warwick NY scraper started")
            
        except Exception as e:
            logger.error(f"Failed to start Warwick scraper: {e}")
    
    def start_dual_scrapers(self):
        """Start both scrapers"""
        logger.info("Starting dual scraper system...")
        
        # Start Plano scraper (runs at 8:00 AM)
        self.start_plano_scraper()
        
        # Wait a bit before starting Warwick scraper
        time.sleep(5)
        
        # Start Warwick scraper (runs at 9:00 AM)
        self.start_warwick_scraper()
        
        logger.info("Both scrapers started successfully")
        logger.info("Plano TX scraper: 8:00 AM daily")
        logger.info("Warwick NY scraper: 9:00 AM daily")
    
    def monitor_processes(self):
        """Monitor both processes and restart if needed"""
        while self.running:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    logger.warning(f"{name} scraper stopped unexpectedly, restarting...")
                    if name == 'plano':
                        self.start_plano_scraper()
                    elif name == 'warwick':
                        self.start_warwick_scraper()
            
            time.sleep(60)  # Check every minute
    
    def stop_all(self):
        """Stop all scrapers"""
        logger.info("Stopping all scrapers...")
        self.running = False
        
        for name, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logger.info(f"Stopped {name} scraper")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal")
        self.stop_all()
        sys.exit(0)

def main():
    """Main function"""
    manager = DualScraperManager()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # Start both scrapers
        manager.start_dual_scrapers()
        
        # Monitor and keep running
        manager.monitor_processes()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        manager.stop_all()
    except Exception as e:
        logger.error(f"Error in dual scraper manager: {e}")
        manager.stop_all()

if __name__ == "__main__":
    main()
