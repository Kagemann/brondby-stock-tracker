"""
Production-ready Brøndby IF Stock Tracker
Main application entry point for deployment
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

# Import our modules
from models import get_db, StockData, NewsArticle, Alert, PriceMovement
from stock_tracker import StockTracker
from news_tracker import NewsTracker
from correlation_analyzer import CorrelationAnalyzer
from alert_system import AlertSystem

# Use production config
try:
    from config_production import ProductionConfig as Config
except ImportError:
    from config import Config

# Setup logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Brøndby IF Stock Tracker API",
    description="API for tracking Brøndby IF stock price and news sentiment",
    version="1.0.0",
    docs_url="/docs" if Config.DEBUG else None,
    redoc_url="/redoc" if Config.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
stock_tracker = StockTracker()
news_tracker = NewsTracker()
analyzer = CorrelationAnalyzer()
alert_system = AlertSystem()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Brøndby IF Stock Tracker API",
        "version": "1.0.0",
        "status": "running",
        "environment": "production" if not Config.DEBUG else "development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "stock_symbol": Config.STOCK_SYMBOL,
        "environment": "production" if not Config.DEBUG else "development"
    }

# Stock Data Endpoints
@app.get("/stock/current")
async def get_current_stock_price():
    """Get current stock price"""
    try:
        current_data = stock_tracker.get_current_price()
        if not current_data:
            raise HTTPException(status_code=404, detail="Unable to fetch current stock price")
        
        return {
            "symbol": Config.STOCK_SYMBOL,
            "name": Config.STOCK_NAME,
            "price": current_data['price'],
            "change_percent": current_data['change_percent'],
            "volume": current_data['volume'],
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting current stock price: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stock/history")
async def get_stock_history(days: int = 7):
    """Get historical stock data"""
    try:
        historical_data = stock_tracker.get_historical_data(days=days)
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        return {
            "symbol": Config.STOCK_SYMBOL,
            "period_days": days,
            "data_points": len(historical_data),
            "data": historical_data
        }
    except Exception as e:
        logger.error(f"Error getting stock history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# News Endpoints
@app.get("/news/recent")
async def get_recent_news(hours: int = 24, db: Session = Depends(get_db)):
    """Get recent news articles"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        articles = db.query(NewsArticle).filter(
            NewsArticle.timestamp >= cutoff_time
        ).order_by(NewsArticle.timestamp.desc()).limit(50).all()
        
        return {
            "period_hours": hours,
            "total_articles": len(articles),
            "articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at,
                    "sentiment_score": article.sentiment_score,
                    "sentiment_label": article.sentiment_label,
                    "relevance_score": article.relevance_score,
                    "timestamp": article.timestamp
                }
                for article in articles
            ]
        }
    except Exception as e:
        logger.error(f"Error getting recent news: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/news/sentiment")
async def get_news_sentiment(hours: int = 24):
    """Get news sentiment summary"""
    try:
        summary = news_tracker.get_sentiment_summary(hours=hours)
        if not summary:
            raise HTTPException(status_code=404, detail="No news data available")
        
        return {
            "period_hours": hours,
            "sentiment_summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting news sentiment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Analysis Endpoints
@app.get("/analysis/insights")
async def get_trading_insights():
    """Get trading insights"""
    try:
        insights = analyzer.generate_insights()
        
        return {
            "timestamp": datetime.utcnow(),
            "total_insights": len(insights),
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Error getting trading insights: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Manual Update Endpoints
@app.post("/update/stock")
async def manual_stock_update():
    """Manually trigger stock data update"""
    try:
        result = stock_tracker.update_stock_data()
        return {
            "success": result is not None,
            "message": "Stock data updated successfully" if result else "Failed to update stock data",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error in manual stock update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/update/news")
async def manual_news_update():
    """Manually trigger news data update"""
    try:
        result = news_tracker.update_news_data()
        return {
            "success": True,
            "articles_saved": result,
            "message": f"News data updated successfully. {result} articles saved.",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error in manual news update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
