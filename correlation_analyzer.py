import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from models import StockData, NewsArticle, PriceMovement, SessionLocal
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrelationAnalyzer:
    def __init__(self):
        self.symbol = Config.STOCK_SYMBOL
        
    def get_time_series_data(self, hours=24):
        """Get stock price and news sentiment data for correlation analysis"""
        try:
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get stock data
            stock_data = db.query(StockData).filter(
                StockData.symbol == self.symbol,
                StockData.timestamp >= cutoff_time
            ).order_by(StockData.timestamp.asc()).all()
            
            # Get news data
            news_data = db.query(NewsArticle).filter(
                NewsArticle.timestamp >= cutoff_time
            ).order_by(NewsArticle.timestamp.asc()).all()
            
            db.close()
            
            return stock_data, news_data
            
        except Exception as e:
            logger.error(f"Error getting time series data: {e}")
            return [], []
    
    def calculate_correlation(self, stock_data, news_data, window_hours=2):
        """Calculate correlation between news sentiment and stock price changes"""
        try:
            if not stock_data or not news_data:
                return None
                
            # Create time windows for analysis
            correlations = []
            
            for i, stock_point in enumerate(stock_data[1:], 1):  # Skip first point
                # Get news in the time window before this stock data point
                window_start = stock_point.timestamp - timedelta(hours=window_hours)
                window_end = stock_point.timestamp
                
                # Find news articles in this window
                window_news = [
                    news for news in news_data
                    if window_start <= news.timestamp <= window_end
                ]
                
                if window_news:
                    # Calculate average sentiment for the window
                    avg_sentiment = np.mean([news.sentiment_score for news in window_news])
                    
                    # Calculate price change
                    price_change = stock_point.change_percent
                    
                    correlations.append({
                        'timestamp': stock_point.timestamp,
                        'price_change': price_change,
                        'avg_sentiment': avg_sentiment,
                        'news_count': len(window_news)
                    })
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None
    
    def analyze_news_impact(self, hours=24):
        """Analyze the impact of news on stock price movements"""
        try:
            stock_data, news_data = self.get_time_series_data(hours)
            correlations = self.calculate_correlation(stock_data, news_data)
            
            if not correlations:
                return None
                
            # Calculate overall correlation
            price_changes = [c['price_change'] for c in correlations]
            sentiments = [c['avg_sentiment'] for c in correlations]
            
            if len(price_changes) > 1:
                correlation_coefficient = np.corrcoef(price_changes, sentiments)[0, 1]
            else:
                correlation_coefficient = 0
            
            # Analyze by sentiment category
            positive_news = [c for c in correlations if c['avg_sentiment'] > 0.1]
            negative_news = [c for c in correlations if c['avg_sentiment'] < -0.1]
            neutral_news = [c for c in correlations if -0.1 <= c['avg_sentiment'] <= 0.1]
            
            analysis = {
                'overall_correlation': correlation_coefficient,
                'total_data_points': len(correlations),
                'positive_news_impact': {
                    'count': len(positive_news),
                    'avg_price_change': np.mean([c['price_change'] for c in positive_news]) if positive_news else 0,
                    'avg_sentiment': np.mean([c['avg_sentiment'] for c in positive_news]) if positive_news else 0
                },
                'negative_news_impact': {
                    'count': len(negative_news),
                    'avg_price_change': np.mean([c['price_change'] for c in negative_news]) if negative_news else 0,
                    'avg_sentiment': np.mean([c['avg_sentiment'] for c in negative_news]) if negative_news else 0
                },
                'neutral_news_impact': {
                    'count': len(neutral_news),
                    'avg_price_change': np.mean([c['price_change'] for c in neutral_news]) if neutral_news else 0,
                    'avg_sentiment': np.mean([c['avg_sentiment'] for c in neutral_news]) if neutral_news else 0
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {e}")
            return None
    
    def identify_patterns(self, hours=48):
        """Identify patterns in price movements and news sentiment"""
        try:
            stock_data, news_data = self.get_time_series_data(hours)
            
            if not stock_data:
                return None
                
            patterns = []
            
            # Look for significant price movements
            for i, stock_point in enumerate(stock_data[1:], 1):
                price_change = abs(stock_point.change_percent)
                
                if price_change > Config.PRICE_CHANGE_THRESHOLD * 100:
                    # Find news around this time
                    window_start = stock_point.timestamp - timedelta(hours=4)
                    window_end = stock_point.timestamp + timedelta(hours=2)
                    
                    related_news = [
                        news for news in news_data
                        if window_start <= news.timestamp <= window_end
                    ]
                    
                    if related_news:
                        avg_sentiment = np.mean([news.sentiment_score for news in related_news])
                        
                        pattern = {
                            'timestamp': stock_point.timestamp,
                            'price_change': stock_point.change_percent,
                            'volume': stock_point.volume,
                            'news_count': len(related_news),
                            'avg_sentiment': avg_sentiment,
                            'pattern_type': 'price_spike_with_news',
                            'confidence': min(price_change / (Config.PRICE_CHANGE_THRESHOLD * 100), 1.0)
                        }
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
            return None
    
    def get_market_sentiment_score(self, hours=24):
        """Calculate overall market sentiment score"""
        try:
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent news
            recent_news = db.query(NewsArticle).filter(
                NewsArticle.timestamp >= cutoff_time
            ).all()
            
            db.close()
            
            if not recent_news:
                return None
                
            # Calculate weighted sentiment score
            total_weight = 0
            weighted_sentiment = 0
            
            for news in recent_news:
                # Weight by relevance and recency
                time_weight = 1.0 - (datetime.utcnow() - news.timestamp).total_seconds() / (hours * 3600)
                relevance_weight = news.relevance_score
                
                weight = time_weight * relevance_weight
                weighted_sentiment += news.sentiment_score * weight
                total_weight += weight
            
            if total_weight > 0:
                market_sentiment = weighted_sentiment / total_weight
            else:
                market_sentiment = 0
            
            # Categorize sentiment
            if market_sentiment > 0.2:
                sentiment_category = 'bullish'
            elif market_sentiment < -0.2:
                sentiment_category = 'bearish'
            else:
                sentiment_category = 'neutral'
            
            return {
                'sentiment_score': market_sentiment,
                'sentiment_category': sentiment_category,
                'total_articles': len(recent_news),
                'confidence': min(total_weight / len(recent_news), 1.0) if recent_news else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return None
    
    def generate_insights(self):
        """Generate trading insights based on analysis"""
        try:
            insights = []
            
            # Get market sentiment
            sentiment = self.get_market_sentiment_score()
            if sentiment:
                if sentiment['sentiment_category'] == 'bullish':
                    insights.append({
                        'type': 'sentiment_analysis',
                        'message': f"Market sentiment is bullish ({sentiment['sentiment_score']:.2f}) with {sentiment['total_articles']} recent articles",
                        'confidence': sentiment['confidence'],
                        'recommendation': 'Consider monitoring for positive price movements'
                    })
                elif sentiment['sentiment_category'] == 'bearish':
                    insights.append({
                        'type': 'sentiment_analysis',
                        'message': f"Market sentiment is bearish ({sentiment['sentiment_score']:.2f}) with {sentiment['total_articles']} recent articles",
                        'confidence': sentiment['confidence'],
                        'recommendation': 'Monitor for potential price declines'
                    })
            
            # Get news impact analysis
            impact = self.analyze_news_impact()
            if impact and abs(impact['overall_correlation']) > 0.3:
                insights.append({
                    'type': 'correlation_analysis',
                    'message': f"Strong correlation ({impact['overall_correlation']:.2f}) between news sentiment and price movements",
                    'confidence': abs(impact['overall_correlation']),
                    'recommendation': 'News sentiment appears to significantly impact stock price'
                })
            
            # Get patterns
            patterns = self.identify_patterns()
            if patterns:
                recent_patterns = [p for p in patterns if p['confidence'] > 0.7]
                if recent_patterns:
                    insights.append({
                        'type': 'pattern_analysis',
                        'message': f"Found {len(recent_patterns)} significant price movement patterns",
                        'confidence': np.mean([p['confidence'] for p in recent_patterns]),
                        'recommendation': 'Monitor for similar patterns in future'
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

if __name__ == "__main__":
    analyzer = CorrelationAnalyzer()
    insights = analyzer.generate_insights()
    print("Trading Insights:")
    for insight in insights:
        print(f"- {insight['message']}")
        print(f"  Recommendation: {insight['recommendation']}")
        print(f"  Confidence: {insight['confidence']:.2f}")
        print()
