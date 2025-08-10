#!/usr/bin/env python3
"""
Test script to check sentiment analysis on updated demo news
"""

from news_tracker import NewsTracker
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_demo_news_sentiment():
    """Test sentiment analysis on the updated demo news"""
    
    tracker = NewsTracker()
    demo_articles = tracker.get_demo_news()
    
    print("🧠 Testing Sentiment Analysis on Updated Demo News")
    print("=" * 60)
    
    for i, article in enumerate(demo_articles, 1):
        text = f"{article['title']} {article['description']}"
        score, label = tracker.analyze_sentiment(text)
        
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Sentiment: {label} (score: {score:.4f})")
        print(f"   Text: {text[:80]}...")
        
        # Color coding
        if label == 'positive':
            print(f"   ✅ POSITIVE - Contains positive Danish keywords")
        elif label == 'negative':
            print(f"   ❌ NEGATIVE - Contains negative Danish keywords")
        else:
            print(f"   ⚪ NEUTRAL - No strong sentiment indicators")

if __name__ == "__main__":
    test_demo_news_sentiment()
