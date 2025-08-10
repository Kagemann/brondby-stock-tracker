import schedule
import time
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from stock_tracker import StockTracker
from news_tracker import NewsTracker
from correlation_analyzer import CorrelationAnalyzer
from alert_system import AlertSystem
from models import create_tables
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.stock_tracker = StockTracker()
        self.news_tracker = NewsTracker()
        self.analyzer = CorrelationAnalyzer()
        self.alert_system = AlertSystem()
        
    def update_stock_data(self):
        """Update stock price data"""
        try:
            logger.info("Updating stock data...")
            result = self.stock_tracker.update_stock_data()
            if result:
                logger.info(f"Stock data updated successfully: {result}")
            else:
                logger.warning("Failed to update stock data")
        except Exception as e:
            logger.error(f"Error updating stock data: {e}")
    
    def update_news_data(self):
        """Update news data"""
        try:
            logger.info("Updating news data...")
            result = self.news_tracker.update_news_data()
            logger.info(f"News data updated: {result} articles saved")
        except Exception as e:
            logger.error(f"Error updating news data: {e}")
    
    def run_analysis(self):
        """Run correlation analysis"""
        try:
            logger.info("Running correlation analysis...")
            insights = self.analyzer.generate_insights()
            logger.info(f"Analysis complete: {len(insights)} insights generated")
            
            # Log insights
            for insight in insights:
                logger.info(f"Insight: {insight['message']}")
                
        except Exception as e:
            logger.error(f"Error running analysis: {e}")
    
    def check_alerts(self):
        """Check and send alerts"""
        try:
            logger.info("Checking alerts...")
            alerts_sent = self.alert_system.run_alert_checks()
            logger.info(f"Alert check complete: {alerts_sent} alerts sent")
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def generate_daily_report(self):
        """Generate daily summary report"""
        try:
            logger.info("Generating daily report...")
            
            # Get stock summary
            stock_summary = self.stock_tracker.get_price_summary(days=1)
            
            # Get news summary
            news_summary = self.news_tracker.get_sentiment_summary(hours=24)
            
            # Get market sentiment
            market_sentiment = self.analyzer.get_market_sentiment_score(hours=24)
            
            # Generate report
            report = f"📊 <b>Daily Report: {Config.STOCK_NAME}</b>\n"
            report += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            if stock_summary:
                report += f"💰 <b>Stock Performance:</b>\n"
                report += f"Current Price: {stock_summary['current_price']:.2f} DKK\n"
                report += f"Daily Change: {stock_summary['total_change']:+.2f}%\n"
                report += f"High: {stock_summary['highest_price']:.2f} DKK\n"
                report += f"Low: {stock_summary['lowest_price']:.2f} DKK\n"
                report += f"Avg Volume: {stock_summary['avg_volume']:,.0f}\n\n"
            
            if news_summary:
                report += f"📰 <b>News Sentiment:</b>\n"
                report += f"Total Articles: {news_summary['total_articles']}\n"
                report += f"Positive: {news_summary['positive_articles']}\n"
                report += f"Negative: {news_summary['negative_articles']}\n"
                report += f"Neutral: {news_summary['neutral_articles']}\n"
                report += f"Avg Sentiment: {news_summary['avg_sentiment']:.2f}\n\n"
            
            if market_sentiment:
                report += f"🎯 <b>Market Sentiment:</b>\n"
                report += f"Score: {market_sentiment['sentiment_score']:.2f}\n"
                report += f"Category: {market_sentiment['sentiment_category'].title()}\n"
                report += f"Confidence: {market_sentiment['confidence']:.2f}\n\n"
            
            # Send report via Telegram
            self.alert_system.send_telegram_alert(report)
            
            logger.info("Daily report generated and sent")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def setup_schedule(self):
        """Setup the scheduling jobs"""
        try:
            # Stock data updates (every 5 minutes during market hours)
            self.scheduler.add_job(
                self.update_stock_data,
                IntervalTrigger(minutes=Config.STOCK_UPDATE_INTERVAL // 60),
                id='stock_update',
                name='Update Stock Data',
                replace_existing=True
            )
            
            # News data updates (every 30 minutes)
            self.scheduler.add_job(
                self.update_news_data,
                IntervalTrigger(minutes=Config.NEWS_UPDATE_INTERVAL // 60),
                id='news_update',
                name='Update News Data',
                replace_existing=True
            )
            
            # Analysis runs (every hour)
            self.scheduler.add_job(
                self.run_analysis,
                IntervalTrigger(minutes=Config.SENTIMENT_UPDATE_INTERVAL // 60),
                id='analysis',
                name='Run Analysis',
                replace_existing=True
            )
            
            # Alert checks (every 10 minutes)
            self.scheduler.add_job(
                self.check_alerts,
                IntervalTrigger(minutes=10),
                id='alert_check',
                name='Check Alerts',
                replace_existing=True
            )
            
            # Daily report (every day at 18:00)
            self.scheduler.add_job(
                self.generate_daily_report,
                'cron',
                hour=18,
                minute=0,
                id='daily_report',
                name='Generate Daily Report',
                replace_existing=True
            )
            
            logger.info("Scheduler setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up scheduler: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            # Create database tables
            create_tables()
            logger.info("Database tables created")
            
            # Setup schedule
            self.setup_schedule()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
            # Run initial data collection
            logger.info("Running initial data collection...")
            self.update_stock_data()
            self.update_news_data()
            self.run_analysis()
            
            logger.info("Initial data collection complete")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        try:
            jobs = self.scheduler.get_jobs()
            status = []
            
            for job in jobs:
                status.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time,
                    'active': job.next_run_time is not None
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return []

def main():
    """Main function to run the scheduler"""
    scheduler = DataScheduler()
    
    try:
        scheduler.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        scheduler.stop()

if __name__ == "__main__":
    main()
