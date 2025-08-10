# 🚀 Brøndby IF Stock Tracker - Deployment Ready!

This project is ready for deployment to various platforms.

## Quick Deploy Options

### Railway (Recommended)
1. Visit [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Add environment variables in Railway dashboard

### Heroku
```bash
heroku create your-brondby-tracker
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Vercel
1. Visit [vercel.com](https://vercel.com)
2. Import this repository
3. Deploy automatically

## Environment Variables Needed

Set these in your deployment platform:

```env
NEWS_API_KEY=your_news_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /stock/current` - Current stock price
- `GET /stock/history?days=7` - Historical stock data
- `GET /news/recent?hours=24` - Recent news
- `GET /news/sentiment?hours=24` - News sentiment
- `GET /analysis/insights` - Trading insights

## Documentation

See `DEPLOYMENT.md` for detailed deployment instructions.