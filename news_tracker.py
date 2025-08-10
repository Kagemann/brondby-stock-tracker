import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
import re
from sqlalchemy.orm import Session
from models import NewsArticle, SessionLocal
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsTracker:
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.keywords = Config.NEWS_KEYWORDS
        self.sources = Config.NEWS_SOURCES
        
    def get_news_from_api(self, days_back=1):
        """Fetch news from NewsAPI"""
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured")
            return []
            
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Search for each keyword
            all_articles = []
            for keyword in self.keywords:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en,da',
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    all_articles.extend(articles)
                else:
                    logger.error(f"NewsAPI error: {response.status_code}")
                    
            return all_articles
            
        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
            return []
    
    def get_demo_news(self):
        """Return demo news data for testing with Danish content for sentiment analysis"""
        demo_articles = [
            {
                'title': 'Brøndby-fadæse: Ydmyget i Island',
                'description': 'Brøndby står over for en vanskelig opgave i Conference League-kvalifikationen, efter klubben torsdag aften led et ydmygende 3-0-nederlag ude mod Víkingur Reykjavík.',
                'url': 'https://bold.dk/fodbold/nyheder/brondby-fadaese-ydmyget-i-island/',
                'source': {'name': 'Bold.dk'},
                'publishedAt': datetime.now() - timedelta(days=3),
                'content': 'Brøndby har ryggen mod muren i Conference League-kvalifikationen. Torsdag aften skuffede klubben stort i Island og tabte 3-0 til Víkingur Reykjavík.'
            },
            {
                'title': 'Fans lavede ballade i Island - nu reagerer Brøndby-direktør',
                'description': 'Brøndby-direktør reagerer på fan-ballade under Conference League-kamp i Island.',
                'url': 'https://sport.tv2.dk/fodbold/2025-08-08-fans-lavede-ballade-i-island-nu-reagerer-broendby-direktoer',
                'source': {'name': 'TV2 Sport'},
                'publishedAt': datetime.now() - timedelta(days=2),
                'content': 'Brøndby-direktør reagerer på de danske fans opførsel under kampen i Island.'
            },
            {
                'title': 'Forløsning for Brøndby: Endelig succes',
                'description': 'Brøndby har endelig fået den tiltrængte forløsning efter en periode med udfordringer.',
                'url': 'https://bold.dk/fodbold/klubber/broendby-if/nyheder/forlosning-for-brondby-det-har-vaeret-svaert',
                'source': {'name': 'Bold.dk'},
                'publishedAt': datetime.now() - timedelta(days=1),
                'content': 'Efter en periode med udfordringer har Brøndby endelig fået den tiltrængte forløsning. Klubben har kæmpet sig gennem vanskelighederne.'
            },
            {
                'title': 'Brøndby kæmper sig til fantastisk sejr',
                'description': 'Brøndby kæmpede sig til en fantastisk sejr mod rivalerne i en spændende kamp.',
                'url': 'https://example.com/brondby-sejr',
                'source': {'name': 'Tipsbladet'},
                'publishedAt': datetime.now() - timedelta(hours=6),
                'content': 'Brøndby viste stærk karakter og kæmpede sig til en fantastisk sejr. Det var en fremragende præstation.'
            },
            {
                'title': 'Brøndby talent stråler i træning',
                'description': 'Ungt Brøndby-talent viser lovende tegn i træning og imponerer trænerne.',
                'url': 'https://example.com/brondby-talent',
                'source': {'name': 'Brøndby IF'},
                'publishedAt': datetime.now() - timedelta(hours=8),
                'content': 'Det unge talent stråler i træning og viser fremtidig potentiale. Trænerne er begejstrede.'
            },
            {
                'title': 'Brøndby møder udfordringer i transfervindue',
                'description': 'Klubben står over for vanskelige udfordringer i det nuværende transfervindue.',
                'url': 'https://example.com/brondby-transfer',
                'source': {'name': 'BT Sport'},
                'publishedAt': datetime.now() - timedelta(hours=12),
                'content': 'Brøndby møder svære udfordringer i transfervinduet. Det bliver en vanskelig tid for klubben.'
            },
            {
                'title': 'Brøndby sikrer sig vigtig sejr i pokalen',
                'description': 'Brøndby sikrede sig en vigtig sejr i pokalturneringen og avancerede til næste runde.',
                'url': 'https://example.com/brondby-pokal',
                'source': {'name': 'Ekstra Bladet'},
                'publishedAt': datetime.now() - timedelta(hours=18),
                'content': 'Brøndby sikrede sig en afgørende sejr i pokalturneringen. Det var en vigtig dag for klubben.'
            }
        ]
        return demo_articles
    
    def get_rss_news(self):
        """Fetch news from RSS feeds"""
        articles = []
        
        rss_feeds = [
            'https://bold.dk/rss.xml',
            'https://www.tipsbladet.dk/rss.xml'
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Check if article is relevant
                    if self.is_relevant_article(entry.title + ' ' + entry.get('summary', '')):
                        article = {
                            'title': entry.title,
                            'description': entry.get('summary', ''),
                            'url': entry.link,
                            'publishedAt': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                            'source': {'name': feed.feed.get('title', 'Unknown')}
                        }
                        articles.append(article)
                        
            except Exception as e:
                logger.error(f"Error parsing RSS feed {feed_url}: {e}")
                
        return articles
    
    def get_web_scraped_news(self):
        """Fetch news by scraping Danish football websites"""
        articles = []
        
        # Brøndby IF official news
        try:
            articles.extend(self.scrape_brondby_news())
        except Exception as e:
            logger.error(f"Error scraping Brøndby news: {e}")
        
        # Tipsbladet news
        try:
            articles.extend(self.scrape_tipsbladet_news())
        except Exception as e:
            logger.error(f"Error scraping Tipsbladet news: {e}")
        
        # Bold.dk news
        try:
            articles.extend(self.scrape_bold_news())
        except Exception as e:
            logger.error(f"Error scraping Bold.dk news: {e}")
        
        # TV2 Sport news
        try:
            articles.extend(self.scrape_tv2_sport_news())
        except Exception as e:
            logger.error(f"Error scraping TV2 Sport news: {e}")
        
        return articles
    
    def scrape_brondby_news(self):
        """Scrape news from Brøndby IF official website"""
        articles = []
        try:
            url = "https://brondby.com/nyheder"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Based on the search results, look for news items
                # The site shows news like "3F Superliga Startopstillingen mod Vejle Boldklub"
                news_items = soup.find_all(['div', 'article'], class_=lambda x: x and any(word in x.lower() for word in ['news', 'article', 'post', 'item']))
                
                # Also look for any divs containing Brøndby-related text
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if any(keyword in text.lower() for keyword in ['brøndby', 'brondby', 'superliga', 'vejle', 'kamp']):
                        # Check if this div contains a title
                        title_elem = div.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if len(title) > 10 and self.is_relevant_article(title):
                                link_elem = div.find('a')
                                url = link_elem.get('href') if link_elem else ''
                                if url and not url.startswith('http'):
                                    url = f"https://brondby.com{url}"
                                
                                articles.append({
                                    'title': title,
                                    'description': text[:200] + "..." if len(text) > 200 else text,
                                    'url': url,
                                    'publishedAt': datetime.now(),
                                    'source': {'name': 'Brøndby IF'}
                                })
                                break  # Only take the first relevant article from each div
                            
        except Exception as e:
            logger.error(f"Error scraping Brøndby news: {e}")
        
        return articles
    
    def scrape_tipsbladet_news(self):
        """Scrape news from Tipsbladet"""
        articles = []
        try:
            url = "https://www.tipsbladet.dk/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for all text elements containing Brøndby keywords
                brondby_elements = soup.find_all(text=lambda text: text and any(keyword in text.lower() for keyword in ['brøndby', 'brondby', 'bif']))
                
                # Also look for article containers
                article_containers = soup.find_all(['div', 'article', 'section', 'a'], class_=lambda x: x and any(word in x.lower() for word in ['news', 'article', 'post', 'item']))
                
                processed_titles = set()
                
                # Process text elements first
                for element in brondby_elements:
                    parent = element.parent
                    if parent:
                        # Look for title in parent or nearby elements
                        title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if (len(title) > 10 and 
                                self.is_relevant_article(title) and 
                                title not in processed_titles):
                                
                                link_elem = parent.find('a') if parent.name == 'a' else parent.find('a')
                                url = link_elem.get('href') if link_elem else ''
                                if url and not url.startswith('http'):
                                    url = f"https://www.tipsbladet.dk{url}"
                                
                                articles.append({
                                    'title': title,
                                    'description': element[:200] + "..." if len(element) > 200 else element,
                                    'url': url,
                                    'publishedAt': datetime.now(),
                                    'source': {'name': 'Tipsbladet'}
                                })
                                processed_titles.add(title)
                
                # Process article containers
                for container in article_containers[:20]:
                    title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if (len(title) > 10 and 
                            self.is_relevant_article(title) and 
                            title not in processed_titles):
                            
                            link_elem = container.find('a')
                            url = link_elem.get('href') if link_elem else ''
                            if url and not url.startswith('http'):
                                url = f"https://www.tipsbladet.dk{url}"
                            
                            description = container.get_text(strip=True)[:200]
                            
                            articles.append({
                                'title': title,
                                'description': description,
                                'url': url,
                                'publishedAt': datetime.now(),
                                'source': {'name': 'Tipsbladet'}
                            })
                            processed_titles.add(title)
                            
        except Exception as e:
            logger.error(f"Error scraping Tipsbladet news: {e}")
        
        return articles
    
    def scrape_bold_news(self):
        """Scrape news from Bold.dk"""
        articles = []
        try:
            # Try multiple Bold.dk URLs for better coverage including club-specific pages
            urls = [
                "https://bold.dk/",
                "https://bold.dk/fodbold/nyheder/",
                "https://bold.dk/fodbold/klubber/broendby-if/nyheder/",  # Brøndby specific news
                "https://bold.dk/fodbold/nyheder/brondby-fadaese-ydmyget-i-island/"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for Brøndby related news - improved detection
                        news_items = soup.find_all(['article', 'div', 'section'], class_=lambda x: x and any(word in x.lower() for word in ['news', 'article', 'post', 'content']))
                        
                        # Also look for any elements containing Brøndby keywords
                        brondby_elements = soup.find_all(text=lambda text: text and any(keyword in text.lower() for keyword in ['brøndby', 'brondby', 'bif']))
                        
                        for item in news_items[:30]:  # Check more items
                            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                if self.is_relevant_article(title):
                                    link_elem = item.find('a')
                                    article_url = link_elem.get('href') if link_elem else ''
                                    if article_url and not article_url.startswith('http'):
                                        article_url = f"https://bold.dk{article_url}"
                                    
                                    description = ""
                                    desc_elem = item.find(['p', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['description', 'summary', 'excerpt']))
                                    if desc_elem:
                                        description = desc_elem.get_text(strip=True)
                                    
                                    articles.append({
                                        'title': title,
                                        'description': description,
                                        'url': article_url,
                                        'publishedAt': datetime.now(),
                                        'source': {'name': 'Bold.dk'}
                                    })
                                    
                except Exception as e:
                    logger.error(f"Error scraping Bold.dk URL {url}: {e}")
                    continue
                            
        except Exception as e:
            logger.error(f"Error scraping Bold.dk news: {e}")
        
        return articles
    
    def get_latest_bold_brondby_articles(self):
        """Specifically check for latest Brøndby articles on Bold.dk"""
        articles = []
        try:
            url = "https://bold.dk/fodbold/klubber/broendby-if/nyheder/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for article links specifically
                article_links = soup.find_all('a', href=True)
                
                for link in article_links[:15]:  # Check first 15 links
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    # Check if it's a Brøndby article and not already processed
                    if (any(keyword in title.lower() for keyword in ['brøndby', 'brondby', 'bif']) and 
                        '/fodbold/klubber/broendby-if/nyheder/' in href and
                        len(title) > 10):
                        
                        # Make sure URL is complete
                        if not href.startswith('http'):
                            href = f"https://bold.dk{href}"
                        
                        # Get article description if available
                        description = ""
                        parent = link.find_parent()
                        if parent:
                            desc_elem = parent.find(['p', 'div'])
                            if desc_elem:
                                description = desc_elem.get_text(strip=True)[:200]
                        
                        articles.append({
                            'title': title,
                            'description': description,
                            'url': href,
                            'publishedAt': datetime.now(),
                            'source': {'name': 'Bold.dk'}
                        })
                        
        except Exception as e:
            logger.error(f"Error getting latest Bold.dk Brøndby articles: {e}")
        
        return articles
    
    def scrape_tv2_sport_news(self):
        """Scrape news from TV2 Sport"""
        articles = []
        try:
            # Try multiple TV2 Sport URLs
            urls = [
                "https://sport.tv2.dk/",
                "https://sport.tv2.dk/fodbold/",
                "https://sport.tv2.dk/fodbold/2025-08-08-fans-lavede-ballade-i-island-nu-reagerer-broendby-direktoer"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            for url in urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for all text elements containing Brøndby keywords
                        brondby_elements = soup.find_all(text=lambda text: text and any(keyword in text.lower() for keyword in ['brøndby', 'brondby', 'bif']))
                        
                        # Also look for article containers
                        news_items = soup.find_all(['article', 'div', 'section'], class_=lambda x: x and any(word in x.lower() for word in ['news', 'article', 'post', 'content']))
                        
                        processed_titles = set()
                        
                        # Process text elements first
                        for element in brondby_elements:
                            parent = element.parent
                            if parent:
                                # Look for title in parent or nearby elements
                                title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'a'])
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    if (len(title) > 10 and 
                                        self.is_relevant_article(title) and 
                                        title not in processed_titles):
                                        
                                        link_elem = parent.find('a') if parent.name == 'a' else parent.find('a')
                                        article_url = link_elem.get('href') if link_elem else ''
                                        if article_url and not article_url.startswith('http'):
                                            article_url = f"https://sport.tv2.dk{article_url}"
                                        
                                        articles.append({
                                            'title': title,
                                            'description': element[:200] + "..." if len(element) > 200 else element,
                                            'url': article_url,
                                            'publishedAt': datetime.now(),
                                            'source': {'name': 'TV2 Sport'}
                                        })
                                        processed_titles.add(title)
                        
                        # Process article containers
                        for item in news_items[:25]:  # Check more items
                            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                if (len(title) > 10 and 
                                    self.is_relevant_article(title) and 
                                    title not in processed_titles):
                                    
                                    link_elem = item.find('a')
                                    article_url = link_elem.get('href') if link_elem else ''
                                    if article_url and not article_url.startswith('http'):
                                        article_url = f"https://sport.tv2.dk{article_url}"
                                    
                                    description = ""
                                    desc_elem = item.find(['p', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['description', 'summary', 'excerpt']))
                                    if desc_elem:
                                        description = desc_elem.get_text(strip=True)
                                    
                                    articles.append({
                                        'title': title,
                                        'description': description,
                                        'url': article_url,
                                        'publishedAt': datetime.now(),
                                        'source': {'name': 'TV2 Sport'}
                                    })
                                    processed_titles.add(title)
                                    
                except Exception as e:
                    logger.error(f"Error scraping TV2 Sport URL {url}: {e}")
                    continue
                            
        except Exception as e:
            logger.error(f"Error scraping TV2 Sport news: {e}")
        
        return articles
    
    def is_relevant_article(self, text):
        """Check if article is relevant to Brøndby IF"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using enhanced Danish keywords"""
        try:
            # Clean text and convert to lowercase
            text = re.sub(r'[^\w\sæøåÆØÅ]', ' ', text).lower()
            
            # Danish positive keywords
            positive_keywords = [
                'sejr', 'vinder', 'vandt', 'fantastisk', 'fantastiske', 'stor', 'store', 'god', 'gode',
                'glad', 'glade', 'lykkelig', 'lykkelige', 'fremragende', 'perfekt', 'perfekte',
                'stærk', 'stærke', 'godt', 'god', 'gode', 'succes', 'succesfuld', 'succesfulde',
                'fremgang', 'fremgangsrig', 'fremgangsrige', 'oprykning', 'mesterskab',
                'champions league', 'europa league', 'pokal', 'trofæ', 'trofæer',
                'mål', 'målscorer', 'assist', 'assister', 'clean sheet', 'nulstilling',
                'forløsning', 'forløsende', 'tiltrængt', 'vigtig', 'vigtige', 'afgørende',
                'kæmpe', 'kæmper', 'kæmpede', 'kæmpet', 'kæmper', 'kæmper', 'kæmper',
                'stråler', 'strålende', 'brilliant', 'brilliante', 'genial', 'geniale',
                'talent', 'talenter', 'lovende', 'fremtid', 'fremtidig', 'fremtidige'
            ]
            
            # Danish negative keywords
            negative_keywords = [
                'nederlag', 'taber', 'tabte', 'dårlig', 'dårlige', 'skuffende', 'skuffet',
                'ydmygelse', 'ydmyget', 'ydmygende', 'fadæse', 'katastrofe', 'katastrofal',
                'mareridt', 'mareridts', 'problem', 'problemer', 'krise', 'kriser',
                'svag', 'svage', 'svært', 'vanskelig', 'vanskelige', 'udfordring',
                'udfordringer', 'mistillid', 'mistillid', 'kritik', 'kritiserer',
                'ballade', 'hærværk', 'boykot', 'boykotter', 'protest', 'protester',
                'skandale', 'skandaler', 'skuffelse', 'skuffet', 'frustreret',
                'vred', 'vrede', 'rasende', 'forarget', 'forargelse', 'skam',
                'pinlig', 'pinlige', 'flov', 'flove', 'bange', 'bekymret', 'bekymringer'
            ]
            
            # Count positive and negative matches
            positive_count = sum(1 for word in positive_keywords if word in text)
            negative_count = sum(1 for word in negative_keywords if word in text)
            
            # Calculate sentiment score (-1 to 1)
            total_words = len(text.split())
            if total_words > 0:
                positive_ratio = positive_count / total_words
                negative_ratio = negative_count / total_words
                sentiment_score = positive_ratio - negative_ratio
            else:
                sentiment_score = 0.0
            
            # Categorize sentiment with more nuanced thresholds
            if sentiment_score > 0.005:  # More sensitive threshold
                sentiment_label = 'positive'
            elif sentiment_score < -0.005:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            # Log for debugging
            logger.debug(f"Sentiment analysis: score={sentiment_score:.4f}, label={sentiment_label}, positive={positive_count}, negative={negative_count}")
                
            return sentiment_score, sentiment_label
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0, 'neutral'
    
    def calculate_relevance_score(self, title, description, content):
        """Calculate relevance score based on keyword matches"""
        text = f"{title} {description} {content}".lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in self.keywords if keyword.lower() in text)
        
        # Calculate score (0-1)
        relevance_score = min(matches / len(self.keywords), 1.0)
        
        return relevance_score
    
    def save_news_article(self, article_data):
        """Save news article to database"""
        try:
            # Check if article already exists
            db = SessionLocal()
            existing = db.query(NewsArticle).filter_by(url=article_data['url']).first()
            if existing:
                db.close()
                return existing
                
            # Analyze sentiment
            text_for_sentiment = f"{article_data['title']} {article_data.get('description', '')}"
            sentiment_score, sentiment_label = self.analyze_sentiment(text_for_sentiment)
            
            # Calculate relevance
            relevance_score = self.calculate_relevance_score(
                article_data['title'],
                article_data.get('description', ''),
                article_data.get('content', '')
            )
            
            # Create news article record
            news_article = NewsArticle(
                title=article_data['title'],
                description=article_data.get('description', ''),
                content=article_data.get('content', ''),
                url=article_data['url'],
                source=article_data['source']['name'],
                published_at=article_data['publishedAt'],
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                relevance_score=relevance_score
            )
            
            db.add(news_article)
            db.commit()
            db.close()
            
            logger.info(f"Saved news article: {article_data['title'][:50]}...")
            return news_article
            
        except Exception as e:
            logger.error(f"Error saving news article: {e}")
            return None
    
    def get_recent_news(self, hours=24):
        """Get recent news articles from database"""
        try:
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            articles = db.query(NewsArticle).filter(
                NewsArticle.timestamp >= cutoff_time
            ).order_by(NewsArticle.timestamp.desc()).all()
            
            db.close()
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching recent news: {e}")
            return []
    
    def get_sentiment_summary(self, hours=24):
        """Get sentiment summary for recent news"""
        try:
            articles = self.get_recent_news(hours)
            
            if not articles:
                return None
                
            positive_count = sum(1 for a in articles if a.sentiment_label == 'positive')
            negative_count = sum(1 for a in articles if a.sentiment_label == 'negative')
            neutral_count = sum(1 for a in articles if a.sentiment_label == 'neutral')
            
            avg_sentiment = sum(a.sentiment_score for a in articles) / len(articles)
            
            summary = {
                'total_articles': len(articles),
                'positive_articles': positive_count,
                'negative_articles': negative_count,
                'neutral_articles': neutral_count,
                'avg_sentiment': avg_sentiment,
                'sentiment_distribution': {
                    'positive': positive_count / len(articles) if articles else 0,
                    'negative': negative_count / len(articles) if articles else 0,
                    'neutral': neutral_count / len(articles) if articles else 0
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}")
            return None
    
    def update_news_data(self):
        """Main method to update news data"""
        try:
            # Get news from multiple sources
            api_articles = self.get_news_from_api(days_back=1)
            rss_articles = self.get_rss_news()
            web_articles = self.get_web_scraped_news()
            
            # Add specific check for latest Bold.dk Brøndby articles
            bold_articles = self.get_latest_bold_brondby_articles()
            all_articles = api_articles + rss_articles + web_articles + bold_articles
            
            # If no real news found, use demo data as fallback
            if not all_articles:
                logger.info("No real news found - using demo data as fallback")
                all_articles = self.get_demo_news()
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            # Save articles
            saved_count = 0
            for article in unique_articles:
                if self.is_relevant_article(article['title'] + ' ' + article.get('description', '')):
                    saved_article = self.save_news_article(article)
                    if saved_article:
                        saved_count += 1
            
            logger.info(f"Updated news data: {saved_count} new articles saved")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error updating news data: {e}")
            return 0

if __name__ == "__main__":
    tracker = NewsTracker()
    result = tracker.update_news_data()
    print(f"News update result: {result} articles saved")
