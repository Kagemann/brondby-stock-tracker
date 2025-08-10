#!/usr/bin/env python3
"""
Brøndby IF Stock Tracker - Replit Entry Point
This file serves as the main entry point for Replit deployment
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def run_api():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    subprocess.run([sys.executable, "api.py"])

def run_dashboard():
    """Run the Dash dashboard"""
    print("📊 Starting Dashboard...")
    # Wait a bit for API to start
    time.sleep(3)
    subprocess.run([sys.executable, "dashboard.py"])

def main():
    """Main entry point for Replit"""
    print("🏟️  Brøndby IF Stock Tracker - Replit Edition")
    print("=" * 50)
    
    # Check if we're in Replit
    if os.getenv('REPL_ID'):
        print("✅ Running on Replit")
        print("🌐 Your app will be available at:")
        print(f"   https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER')}.repl.co")
        print("📊 Dashboard will be available at:")
        print(f"   https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER')}.repl.co:8050")
    else:
        print("⚠️  Not running on Replit")
    
    # Check environment variables
    required_vars = ['NEWS_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Set them in Replit Secrets tab")
    else:
        print("✅ All environment variables found")
    
    # Start API server in background
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Start dashboard in background
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    print("\n🎯 Your Brøndby IF Stock Tracker is starting...")
    print("📈 Tracking BIF.CO stock price")
    print("📰 Monitoring Danish football news")
    print("🧠 Analyzing sentiment")
    print("📱 Sending Telegram alerts")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
            print("💚 App is running...")
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()
