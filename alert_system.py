import requests
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Alert, SessionLocal, StockData, NewsArticle
from config import Config
from stock_tracker import StockTracker
from news_tracker import NewsTracker
from correlation_analyzer import CorrelationAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        self.telegram_token = Config.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = Config.TELEGRAM_CHAT_ID
        self.stock_tracker = StockTracker()
        self.news_tracker = NewsTracker()
        self.analyzer = CorrelationAnalyzer()
        
    def send_telegram_alert(self, message, parse_mode='HTML'):
        """Send alert via Telegram bot"""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info("Telegram alert sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram alert: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def check_price_alerts(self):
        """Check for significant price movements"""
        try:
            db = SessionLocal()
            
            # Get latest stock data
            latest_stock = db.query(StockData).filter_by(symbol=Config.STOCK_SYMBOL).order_by(StockData.timestamp.desc()).first()
            
            if not latest_stock:
                db.close()
                return []
                
            # Get previous data point for comparison
            previous_stock = db.query(StockData).filter(
                StockData.symbol == Config.STOCK_SYMBOL,
                StockData.timestamp < latest_stock.timestamp
            ).order_by(StockData.timestamp.desc()).first()
            
            alerts = []
            
            if previous_stock:
                price_change = abs(latest_stock.change_percent)
                volume_change = ((latest_stock.volume - previous_stock.volume) / previous_stock.volume) * 100 if previous_stock.volume > 0 else 0
                
                # Check for significant price movement
                if price_change > Config.PRICE_CHANGE_THRESHOLD * 100:
                    severity = 'high' if price_change > 10 else 'medium'
                    
                    alert_message = f"🚨 <b>Price Alert: {Config.STOCK_NAME}</b>\n\n"
                    alert_message += f"Price: {latest_stock.price:.2f} DKK\n"
                    alert_message += f"Change: {latest_stock.change_percent:+.2f}%\n"
                    alert_message += f"Volume: {latest_stock.volume:,}\n"
                    alert_message += f"Time: {latest_stock.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    # Check if there's recent news
                    recent_news = db.query(NewsArticle).filter(
                        NewsArticle.timestamp >= latest_stock.timestamp - timedelta(hours=4)
                    ).order_by(NewsArticle.timestamp.desc()).limit(3).all()
                    
                    if recent_news:
                        alert_message += "\n\n📰 <b>Recent News:</b>\n"
                        for news in recent_news:
                            sentiment_emoji = "🟢" if news.sentiment_label == 'positive' else "🔴" if news.sentiment_label == 'negative' else "🟡"
                            alert_message += f"{sentiment_emoji} {news.title[:50]}...\n"
                    
                    alerts.append({
                        'type': 'price_spike',
                        'message': alert_message,
                        'severity': severity,
                        'timestamp': latest_stock.timestamp
                    })
                
                # Check for volume surge
                if volume_change > 100:  # 100% volume increase
                    alert_message = f"📊 <b>Volume Alert: {Config.STOCK_NAME}</b>\n\n"
                    alert_message += f"Volume: {latest_stock.volume:,}\n"
                    alert_message += f"Volume Change: {volume_change:+.1f}%\n"
                    alert_message += f"Price: {latest_stock.price:.2f} DKK\n"
                    alert_message += f"Time: {latest_stock.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    alerts.append({
                        'type': 'volume_surge',
                        'message': alert_message,
                        'severity': 'medium',
                        'timestamp': latest_stock.timestamp
                    })
            
            db.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")
            return []
    
    def check_sentiment_alerts(self):
        """Check for significant sentiment changes"""
        try:
            # Get sentiment summary
            sentiment = self.analyzer.get_market_sentiment_score(hours=6)
            
            if not sentiment:
                return []
                
            alerts = []
            
            # Check for extreme sentiment
            if abs(sentiment['sentiment_score']) > 0.5 and sentiment['total_articles'] >= 3:
                if sentiment['sentiment_score'] > 0.5:
                    alert_message = f"🟢 <b>Bullish Sentiment Alert: {Config.STOCK_NAME}</b>\n\n"
                    alert_message += f"Sentiment Score: {sentiment['sentiment_score']:.2f}\n"
                    alert_message += f"Articles: {sentiment['total_articles']}\n"
                    alert_message += f"Confidence: {sentiment['confidence']:.2f}"
                else:
                    alert_message = f"🔴 <b>Bearish Sentiment Alert: {Config.STOCK_NAME}</b>\n\n"
                    alert_message += f"Sentiment Score: {sentiment['sentiment_score']:.2f}\n"
                    alert_message += f"Articles: {sentiment['total_articles']}\n"
                    alert_message += f"Confidence: {sentiment['confidence']:.2f}"
                
                alerts.append({
                    'type': 'sentiment_extreme',
                    'message': alert_message,
                    'severity': 'medium',
                    'timestamp': datetime.utcnow()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking sentiment alerts: {e}")
            return []
    
    def check_correlation_alerts(self):
        """Check for significant correlation patterns"""
        try:
            # Get correlation analysis
            impact = self.analyzer.analyze_news_impact(hours=12)
            
            if not impact:
                return []
                
            alerts = []
            
            # Check for strong correlation
            if abs(impact['overall_correlation']) > 0.6:
                alert_message = f"📈 <b>Correlation Alert: {Config.STOCK_NAME}</b>\n\n"
                alert_message += f"News-Price Correlation: {impact['overall_correlation']:.2f}\n"
                alert_message += f"Data Points: {impact['total_data_points']}\n\n"
                
                if impact['positive_news_impact']['count'] > 0:
                    alert_message += f"Positive News Impact: {impact['positive_news_impact']['avg_price_change']:.2f}%\n"
                if impact['negative_news_impact']['count'] > 0:
                    alert_message += f"Negative News Impact: {impact['negative_news_impact']['avg_price_change']:.2f}%"
                
                alerts.append({
                    'type': 'correlation_pattern',
                    'message': alert_message,
                    'severity': 'low',
                    'timestamp': datetime.utcnow()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking correlation alerts: {e}")
            return []
    
    def save_alert(self, alert_data):
        """Save alert to database"""
        try:
            db = SessionLocal()
            alert = Alert(
                alert_type=alert_data['type'],
                message=alert_data['message'],
                severity=alert_data['severity']
            )
            db.add(alert)
            db.commit()
            db.close()
            return alert
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
            return None
    
    def mark_alert_sent(self, alert_id):
        """Mark alert as sent"""
        try:
            db = SessionLocal()
            alert = db.query(Alert).filter_by(id=alert_id).first()
            if alert:
                alert.is_sent = True
                alert.sent_at = datetime.utcnow()
                db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error marking alert as sent: {e}")
    
    def run_alert_checks(self):
        """Run all alert checks and send notifications"""
        try:
            all_alerts = []
            
            # Check different types of alerts
            price_alerts = self.check_price_alerts()
            sentiment_alerts = self.check_sentiment_alerts()
            correlation_alerts = self.check_correlation_alerts()
            
            all_alerts.extend(price_alerts)
            all_alerts.extend(sentiment_alerts)
            all_alerts.extend(correlation_alerts)
            
            # Send alerts and save to database
            for alert_data in all_alerts:
                # Save to database
                saved_alert = self.save_alert(alert_data)
                
                if saved_alert:
                    # Send via Telegram
                    success = self.send_telegram_alert(alert_data['message'])
                    
                    if success:
                        self.mark_alert_sent(saved_alert.id)
                        logger.info(f"Alert sent: {alert_data['type']}")
                    else:
                        logger.error(f"Failed to send alert: {alert_data['type']}")
            
            return len(all_alerts)
            
        except Exception as e:
            logger.error(f"Error running alert checks: {e}")
            return 0
    
    def get_recent_alerts(self, hours=24):
        """Get recent alerts from database"""
        try:
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            alerts = db.query(Alert).filter(
                Alert.timestamp >= cutoff_time
            ).order_by(Alert.timestamp.desc()).all()
            
            db.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []

if __name__ == "__main__":
    alert_system = AlertSystem()
    alerts_sent = alert_system.run_alert_checks()
    print(f"Sent {alerts_sent} alerts")
