#!/usr/bin/env python3
"""
Test News Collection Script
This script manually triggers news collection to debug the issue
"""

import os
import sys
from news_tracker import NewsTracker
from config import Config

def test_news_collection():
    """Test news collection manually"""
    print("🧪 Testing News Collection...")
    print("=" * 40)
    
    # Check environment variables
    print(f"NEWS_API_KEY: {'✅ Set' if os.getenv('NEWS_API_KEY') else '❌ Missing'}")
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Missing'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ Set' if os.getenv('TELEGRAM_CHAT_ID') else '❌ Missing'}")
    
    # Test news tracker
    try:
        nt = NewsTracker()
        print("\n📰 Testing news sources...")
        
        # Test API news
        print("\n1. Testing NewsAPI:")
        api_news = nt.get_news_from_api(days_back=1)
        print(f"   Found {len(api_news)} articles from API")
        
        # Test RSS news
        print("\n2. Testing RSS feeds:")
        rss_news = nt.get_rss_news()
        print(f"   Found {len(rss_news)} articles from RSS")
        
        # Test web scraping
        print("\n3. Testing web scraping:")
        web_news = nt.get_web_scraped_news()
        print(f"   Found {len(web_news)} articles from web scraping")
        
        # Test full update
        print("\n4. Testing full news update:")
        result = nt.update_news_data()
        print(f"   Total articles saved: {result}")
        
        # Test getting recent news
        print("\n5. Testing recent news retrieval:")
        recent_news = nt.get_recent_news(hours=24)
        print(f"   Found {len(recent_news)} recent articles in database")
        
        if recent_news:
            print("\n📋 Sample articles:")
            for i, article in enumerate(recent_news[:3]):
                print(f"   {i+1}. {article.title[:50]}...")
        
        print("\n✅ News collection test complete!")
        
    except Exception as e:
        print(f"\n❌ Error during news collection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_collection()
