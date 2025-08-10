import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from models import StockData, SessionLocal
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockTracker:
    def __init__(self):
        self.symbol = Config.STOCK_SYMBOL
        self.stock = yf.Ticker(self.symbol)
        
    def get_current_price(self):
        """Get current stock price and basic info"""
        try:
            info = self.stock.info
            current_price = info.get('regularMarketPrice', 0)
            volume = info.get('volume', 0)
            open_price = info.get('regularMarketOpen', 0)
            high_price = info.get('dayHigh', 0)
            low_price = info.get('dayLow', 0)
            close_price = info.get('regularMarketPreviousClose', 0)
            
            # Calculate change percentage
            if close_price and close_price > 0:
                change_percent = ((current_price - close_price) / close_price) * 100
            else:
                change_percent = 0
                
            return {
                'price': current_price,
                'volume': volume,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'change_percent': change_percent
            }
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return None
    
    def get_historical_data(self, days=30):
        """Get historical stock data in the format expected by the API"""
        try:
            # Try to get real historical data
            hist = self.stock.history(period=f"{days}d")
            
            if hist.empty:
                logger.warning(f"No historical data found for {self.symbol}")
                # Generate sample data if no real data is available
                return self.generate_sample_historical_data(days)
            
            data = []
            for index, row in hist.iterrows():
                data.append({
                    'timestamp': index.isoformat(),
                    'price': float(row['Close']),
                    'volume': int(row['Volume']),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low'])
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            # Generate sample data as fallback
            return self.generate_sample_historical_data(days)
    
    def generate_sample_historical_data(self, days=30):
        """Generate sample historical data for demonstration"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        base_price = 0.323  # Current price
        base_volume = 1000000
        
        for i in range(days):
            # Generate date
            date = datetime.now() - timedelta(days=days-i-1)
            
            # Add some realistic price variation
            price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            price = base_price * (1 + price_change)
            
            # Add some volume variation
            volume_change = random.uniform(0.5, 1.5)
            volume = int(base_volume * volume_change)
            
            # Generate OHLC data
            daily_change = random.uniform(-0.02, 0.02)
            open_price = price * (1 + random.uniform(-0.01, 0.01))
            high_price = max(open_price, price) * (1 + random.uniform(0, 0.03))
            low_price = min(open_price, price) * (1 - random.uniform(0, 0.03))
            
            data.append({
                'timestamp': date.isoformat(),
                'price': round(price, 3),
                'volume': volume,
                'open': round(open_price, 3),
                'high': round(high_price, 3),
                'low': round(low_price, 3)
            })
            
            # Update base price for next iteration
            base_price = price
        
        return data
    
    def save_stock_data(self, stock_data):
        """Save stock data to database"""
        try:
            db = SessionLocal()
            stock_record = StockData(
                symbol=self.symbol,
                price=stock_data['price'],
                volume=stock_data['volume'],
                open_price=stock_data['open_price'],
                high_price=stock_data['high_price'],
                low_price=stock_data['low_price'],
                close_price=stock_data['close_price'],
                change_percent=stock_data['change_percent']
            )
            db.add(stock_record)
            db.commit()
            db.close()
            logger.info(f"Saved stock data: {stock_data['price']} DKK")
            return stock_record
        except Exception as e:
            logger.error(f"Error saving stock data: {e}")
            return None
    
    def get_latest_stock_data(self):
        """Get the most recent stock data from database"""
        try:
            db = SessionLocal()
            latest = db.query(StockData).filter_by(symbol=self.symbol).order_by(StockData.timestamp.desc()).first()
            db.close()
            return latest
        except Exception as e:
            logger.error(f"Error fetching latest stock data: {e}")
            return None
    
    def check_price_movement(self, current_data, previous_data):
        """Check if there's a significant price movement"""
        if not previous_data:
            return None
            
        price_change = abs(current_data['change_percent'])
        volume_change = ((current_data['volume'] - previous_data.volume) / previous_data.volume) * 100 if previous_data.volume > 0 else 0
        
        # Define significant movement thresholds
        price_threshold = Config.PRICE_CHANGE_THRESHOLD * 100  # Convert to percentage
        volume_threshold = 50  # 50% volume increase
        
        if price_change > price_threshold or volume_change > volume_threshold:
            movement_type = 'significant_increase' if current_data['change_percent'] > 0 else 'significant_decrease'
            return {
                'type': movement_type,
                'price_change': current_data['change_percent'],
                'volume_change': volume_change,
                'confidence': min(price_change / price_threshold, 1.0)
            }
        
        return None
    
    def update_stock_data(self):
        """Main method to update stock data"""
        try:
            current_data = self.get_current_price()
            if not current_data:
                return None
                
            # Save current data
            saved_data = self.save_stock_data(current_data)
            
            # Check for significant movements
            previous_data = self.get_latest_stock_data()
            if previous_data and saved_data.id != previous_data.id:
                movement = self.check_price_movement(current_data, previous_data)
                if movement:
                    logger.warning(f"Significant price movement detected: {movement}")
                    return movement
            
            return saved_data
            
        except Exception as e:
            logger.error(f"Error in update_stock_data: {e}")
            return None
    
    def get_price_summary(self, days=7):
        """Get price summary for the last N days"""
        try:
            db = SessionLocal()
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            data = db.query(StockData).filter(
                StockData.symbol == self.symbol,
                StockData.timestamp >= start_date,
                StockData.timestamp <= end_date
            ).order_by(StockData.timestamp.asc()).all()
            
            db.close()
            
            if not data:
                return None
                
            prices = [d.price for d in data]
            volumes = [d.volume for d in data]
            
            summary = {
                'current_price': prices[-1],
                'start_price': prices[0],
                'highest_price': max(prices),
                'lowest_price': min(prices),
                'avg_volume': sum(volumes) / len(volumes),
                'total_change': ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] > 0 else 0,
                'data_points': len(data)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting price summary: {e}")
            return None

if __name__ == "__main__":
    tracker = StockTracker()
    result = tracker.update_stock_data()
    print(f"Stock update result: {result}")
