from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String(20))
    price = Column(Float)
    volume = Column(Integer)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    change_percent = Column(Float)
    
    def __repr__(self):
        return f"<StockData(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    title = Column(String(500))
    description = Column(Text)
    content = Column(Text)
    url = Column(String(500))
    source = Column(String(100))
    published_at = Column(DateTime)
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))  # positive, negative, neutral
    relevance_score = Column(Float)
    
    def __repr__(self):
        return f"<NewsArticle(title='{self.title[:50]}...', sentiment='{self.sentiment_label}')>"

class PriceMovement(Base):
    __tablename__ = 'price_movements'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String(20))
    price_change = Column(Float)
    volume_change = Column(Float)
    movement_type = Column(String(20))  # significant_increase, significant_decrease, normal
    trigger_news_id = Column(Integer)  # Foreign key to news_articles
    confidence_score = Column(Float)
    
    def __repr__(self):
        return f"<PriceMovement(symbol='{self.symbol}', change={self.price_change}, type='{self.movement_type}')>"

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(50))  # price_spike, news_sentiment, volume_surge
    message = Column(Text)
    severity = Column(String(20))  # low, medium, high, critical
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Alert(type='{self.alert_type}', severity='{self.severity}', sent={self.is_sent})>"

# Database setup
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
