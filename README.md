# Brøndby IF Stock Tracker

A comprehensive stock tracking and news sentiment analysis system for Brøndby IF (BRNDBY.CO). This system monitors stock price movements, analyzes news sentiment, and provides insights to help identify price movement patterns.

## 🚀 Features

### Stock Tracking
- Real-time stock price monitoring using Yahoo Finance API
- Historical price data collection and storage
- Volume analysis and price movement detection
- Automated data collection every 5 minutes

### News Analysis
- Multi-source news aggregation (NewsAPI, RSS feeds)
- Sentiment analysis using Natural Language Processing
- Relevance scoring for Brøndby IF related news
- Danish and English news coverage

### Correlation Analysis
- News sentiment correlation with stock price movements
- Pattern identification in price movements
- Market sentiment scoring
- Trading insights generation

### Alert System
- Real-time alerts for significant price movements
- Sentiment-based alerts
- Telegram integration for instant notifications
- Configurable alert thresholds

### API & Dashboard
- RESTful API for data access
- Comprehensive dashboard endpoints
- Real-time data visualization
- Historical analysis capabilities

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **Database**: SQLite (local), PostgreSQL (production)
- **Data Processing**: Pandas, NumPy
- **News & Sentiment**: NewsAPI, TextBlob, NLTK
- **Stock Data**: Yahoo Finance API
- **Scheduling**: APScheduler
- **Notifications**: Telegram Bot API
- **API Documentation**: FastAPI auto-generated docs

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys for:
  - NewsAPI (free tier available)
  - Telegram Bot (optional, for notifications)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd brondby-stock-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your API keys:
   ```env
   NEWS_API_KEY=your_newsapi_key_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   ```

5. **Initialize database**
   ```bash
   python -c "from models import create_tables; create_tables()"
   ```

## 🚀 Usage

### Starting the Scheduler (Recommended)
Run the automated data collection and analysis:
```bash
python scheduler.py
```

This will:
- Start collecting stock data every 5 minutes
- Update news every 30 minutes
- Run analysis every hour
- Check alerts every 10 minutes
- Generate daily reports at 18:00

### Starting the API Server
Run the FastAPI server for data access:
```bash
python api.py
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Manual Data Collection
```bash
# Update stock data
python stock_tracker.py

# Update news data
python news_tracker.py

# Run analysis
python correlation_analyzer.py

# Check alerts
python alert_system.py
```

## 📊 API Endpoints

### Stock Data
- `GET /stock/current` - Current stock price
- `GET /stock/history?days=7` - Historical stock data
- `GET /stock/summary?days=7` - Stock price summary

### News Data
- `GET /news/recent?hours=24` - Recent news articles
- `GET /news/sentiment?hours=24` - News sentiment summary

### Analysis
- `GET /analysis/sentiment?hours=24` - Market sentiment
- `GET /analysis/correlation?hours=24` - News-price correlation
- `GET /analysis/insights` - Trading insights
- `GET /analysis/patterns?hours=48` - Price patterns

### Alerts
- `GET /alerts/recent?hours=24` - Recent alerts

### Dashboard
- `GET /dashboard` - Comprehensive dashboard data

### Manual Updates
- `POST /update/stock` - Manual stock update
- `POST /update/news` - Manual news update
- `POST /alerts/check` - Manual alert check

## 🔔 Alert Configuration

Alerts are triggered for:
- **Price Movements**: >5% price change (configurable)
- **Volume Surges**: >100% volume increase
- **Sentiment Extremes**: >0.5 sentiment score with 3+ articles
- **Correlation Patterns**: >0.6 correlation coefficient

## 📈 Data Sources

### Stock Data
- **Primary**: Yahoo Finance API (BRNDBY.CO)
- **Backup**: Alpha Vantage API (optional)

### News Sources
- **Danish Media**: DR.dk, TV2.dk, Bold.dk, Tipsbladet.dk
- **International**: UEFA.com, general sports news
- **RSS Feeds**: Multiple Danish sports feeds
- **NewsAPI**: Global news search

## 🎯 Key Features for Trading

### Price Movement Detection
- Real-time monitoring of significant price changes
- Volume analysis for unusual trading activity
- Historical pattern recognition

### News Sentiment Analysis
- Automated sentiment scoring of news articles
- Relevance filtering for Brøndby IF specific news
- Correlation analysis with price movements

### Market Insights
- Bullish/bearish sentiment categorization
- News impact quantification
- Pattern identification and confidence scoring

### Alert System
- Instant notifications for significant events
- Contextual information with recent news
- Configurable alert thresholds

## 🔧 Configuration

Edit `config.py` to customize:
- Stock symbol and name
- News sources and keywords
- Update intervals
- Alert thresholds
- Database settings

## 📊 Database Schema

### Tables
- **stock_data**: Historical stock prices and volumes
- **news_articles**: News articles with sentiment analysis
- **price_movements**: Identified significant price movements
- **alerts**: Generated alerts and their status

## 🚀 Deployment

### Local Development
```bash
python scheduler.py  # Background data collection
python api.py        # API server
```

### Production Deployment
1. Use PostgreSQL instead of SQLite
2. Set up proper logging
3. Configure environment variables
4. Use process manager (PM2, Supervisor)
5. Set up monitoring and alerts

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scheduler.py"]
```

## 📝 Logging

Logs are written to `brondby_tracker.log` with configurable levels:
- INFO: General operations
- WARNING: Non-critical issues
- ERROR: Critical errors

## 🔒 Security Considerations

- Store API keys in environment variables
- Use HTTPS in production
- Implement rate limiting
- Regular security updates
- Database access controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## 🆘 Support

For issues and questions:
1. Check the logs in `brondby_tracker.log`
2. Verify API keys are correctly configured
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`

## 🔄 Updates and Maintenance

- Regular dependency updates
- API endpoint monitoring
- Data quality checks
- Performance optimization
- Feature enhancements based on usage patterns
