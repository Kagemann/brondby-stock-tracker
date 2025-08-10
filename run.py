#!/usr/bin/env python3
"""
Brøndby IF Stock Tracker - Main Runner Script

This script provides a simple way to start the stock tracking system.
It can run the scheduler, API server, or both depending on the arguments.
"""

import argparse
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import yfinance
        import pandas
        import requests
        import sqlalchemy
        import apscheduler
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please create .env file with your API keys:")
        print("cp env_example.txt .env")
        print("Then edit .env with your actual API keys")
        return False
    print("✅ .env file found")
    return True

def start_scheduler():
    """Start the data collection scheduler"""
    print("🚀 Starting Brøndby IF Stock Tracker Scheduler...")
    print("This will:")
    print("  - Collect stock data every 5 minutes")
    print("  - Update news every 30 minutes")
    print("  - Run analysis every hour")
    print("  - Check alerts every 10 minutes")
    print("  - Generate daily reports at 18:00")
    print()
    
    try:
        # Import and start scheduler
        from scheduler import DataScheduler
        scheduler = DataScheduler()
        scheduler.start()
        
        print("✅ Scheduler started successfully!")
        print("Press Ctrl+C to stop")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping scheduler...")
            scheduler.stop()
            print("✅ Scheduler stopped")
            
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return False
    
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("🌐 Starting Brøndby IF Stock Tracker API Server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print()
    
    try:
        import uvicorn
        from api import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False
    
    return True

def start_dashboard():
    """Start the web dashboard"""
    print("📊 Starting Brøndby IF Stock Tracker Dashboard...")
    print("Dashboard will be available at: http://localhost:8050")
    print("Make sure the API server is running on port 8000")
    print()
    
    try:
        from dashboard import app
        
        app.run_server(
            debug=True,
            host='0.0.0.0',
            port=8050
        )
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False
    
    return True

def run_initial_setup():
    """Run initial setup tasks"""
    print("🔧 Running initial setup...")
    
    try:
        # Create database tables
        from models import create_tables
        create_tables()
        print("✅ Database tables created")
        
        # Run initial data collection
        print("📊 Running initial data collection...")
        
        from stock_tracker import StockTracker
        from news_tracker import NewsTracker
        
        stock_tracker = StockTracker()
        news_tracker = NewsTracker()
        
        # Get initial stock data
        stock_result = stock_tracker.update_stock_data()
        if stock_result:
            print("✅ Initial stock data collected")
        else:
            print("⚠️  Could not collect initial stock data")
        
        # Get initial news data
        news_result = news_tracker.update_news_data()
        print(f"✅ Initial news data collected: {news_result} articles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in initial setup: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Brøndby IF Stock Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py scheduler          # Start data collection scheduler
  python run.py api               # Start API server
  python run.py dashboard         # Start web dashboard
  python run.py all               # Start scheduler and API server
  python run.py setup             # Run initial setup only
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['scheduler', 'api', 'dashboard', 'all', 'setup'],
        help='Mode to run the application in'
    )
    
    parser.add_argument(
        '--no-check',
        action='store_true',
        help='Skip dependency and environment checks'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏟️  Brøndby IF Stock Tracker")
    print("=" * 60)
    print()
    
    # Check dependencies and environment
    if not args.no_check:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_env_file():
            print("⚠️  Continuing without .env file (some features may not work)")
        print()
    
    # Run based on mode
    if args.mode == 'setup':
        success = run_initial_setup()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'scheduler':
        success = start_scheduler()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'api':
        success = start_api_server()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'dashboard':
        success = start_dashboard()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'all':
        print("🚀 Starting Brøndby IF Stock Tracker (Full Mode)")
        print("This will start both the scheduler and API server")
        print()
        
        # Run initial setup first
        if not run_initial_setup():
            print("❌ Initial setup failed")
            sys.exit(1)
        
        print()
        print("Starting services...")
        print("Scheduler: Background data collection")
        print("API Server: http://localhost:8000")
        print("Dashboard: http://localhost:8050")
        print()
        
        try:
            # Start scheduler in background
            from multiprocessing import Process
            from scheduler import DataScheduler
            
            def run_scheduler():
                scheduler = DataScheduler()
                scheduler.start()
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
            
            scheduler_process = Process(target=run_scheduler)
            scheduler_process.start()
            
            print("✅ Scheduler started in background")
            
            # Start API server in foreground
            print("🌐 Starting API server...")
            start_api_server()
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            if 'scheduler_process' in locals():
                scheduler_process.terminate()
                scheduler_process.join()
            print("✅ All services stopped")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            if 'scheduler_process' in locals():
                scheduler_process.terminate()
            sys.exit(1)

if __name__ == "__main__":
    main()

