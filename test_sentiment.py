#!/usr/bin/env python3
"""
Test script to debug sentiment analysis
"""

from news_tracker import NewsTracker
import logging

# Setup logging to see debug output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_sentiment_analysis():
    """Test the sentiment analysis with various Danish texts"""
    
    tracker = NewsTracker()
    
    # Test cases with Danish football content
    test_cases = [
        {
            'title': 'Brøndby-fadæse: Ydmyget i Island',
            'description': 'Brøndby står over for en vanskelig opgave i Conference League-kvalifikationen, efter klubben torsdag aften led et ydmygende 3-0-nederlag ude mod Víkingur Reykjavík.',
            'expected': 'negative'
        },
        {
            'title': 'Forløsning for Brøndby: Det har været svært',
            'description': 'Brøndby har endelig fået den tiltrængte forløsning efter en svær periode.',
            'expected': 'positive'
        },
        {
            'title': 'Brøndby kæmper sig til sejr',
            'description': 'Brøndby kæmpede sig til en fantastisk sejr mod rivalerne.',
            'expected': 'positive'
        },
        {
            'title': 'Fans lavede ballade i Island',
            'description': 'Danske fans lavede ballade under kampen i Island.',
            'expected': 'negative'
        },
        {
            'title': 'Brøndby IF Announces New Stadium Expansion Plans',
            'description': 'The Danish football club reveals ambitious plans to expand their home stadium capacity.',
            'expected': 'neutral'
        }
    ]
    
    print("🧠 Testing Sentiment Analysis")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        text = f"{test_case['title']} {test_case['description']}"
        score, label = tracker.analyze_sentiment(text)
        
        print(f"\nTest {i}: {test_case['title']}")
        print(f"Text: {text[:100]}...")
        print(f"Expected: {test_case['expected']}")
        print(f"Got: {label} (score: {score:.4f})")
        print(f"Match: {'✅' if label == test_case['expected'] else '❌'}")
    
    # Test with some real Danish keywords
    print("\n" + "=" * 50)
    print("🔍 Testing Individual Keywords")
    
    positive_tests = [
        "sejr", "vinder", "fantastisk", "forløsning", "tiltrængt", "kæmpe", "stærk"
    ]
    
    negative_tests = [
        "nederlag", "fadæse", "ydmyget", "ballade", "problem", "svært"
    ]
    
    print("\nPositive keywords:")
    for word in positive_tests:
        score, label = tracker.analyze_sentiment(f"Brøndby {word} mod rivalerne")
        print(f"  {word}: {label} ({score:.4f})")
    
    print("\nNegative keywords:")
    for word in negative_tests:
        score, label = tracker.analyze_sentiment(f"Brøndby {word} i kampen")
        print(f"  {word}: {label} ({score:.4f})")

if __name__ == "__main__":
    test_sentiment_analysis()
