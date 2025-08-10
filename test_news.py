from news_tracker import NewsTracker

print("Testing enhanced news scraping...")

nt = NewsTracker()

# Test web scraping
print("\n1. Testing web scraping:")
web_articles = nt.get_web_scraped_news()
print(f"Found {len(web_articles)} web scraped articles")
for article in web_articles[:3]:
    print(f"- {article['title']} ({article['source']['name']})")

# Test RSS feeds
print("\n2. Testing RSS feeds:")
rss_articles = nt.get_rss_news()
print(f"Found {len(rss_articles)} RSS articles")
for article in rss_articles[:3]:
    print(f"- {article['title']} ({article['source']['name']})")

# Test full update
print("\n3. Testing full news update:")
result = nt.update_news_data()
print(f"Total articles saved: {result}")
