# 🚀 Brøndby IF Stock Tracker - Deployment Guide

This guide will help you deploy your Brøndby IF Stock Tracker to make it live and accessible from anywhere!

## 📋 **Prerequisites**

1. **GitHub Account** ✅ (You have this)
2. **API Keys** (NewsAPI, Telegram Bot)
3. **Domain Name** (Optional but recommended)

---

## 🎯 **Option 1: Railway Deployment (Recommended)**

Railway is perfect for Python FastAPI applications and offers a generous free tier.

### **Step 1: Prepare Your Repository**

```bash
# Make sure all files are committed to Git
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### **Step 2: Deploy to Railway**

1. **Visit [Railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your repository**
5. **Railway will automatically detect it's a Python app**

### **Step 3: Configure Environment Variables**

In Railway dashboard, go to your project → Variables tab and add:

```env
NEWS_API_KEY=your_news_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DATABASE_URL=postgresql://... (Railway will provide this)
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### **Step 4: Deploy**

Railway will automatically deploy your app! You'll get a URL like:
`https://your-app-name.railway.app`

---

## 🎯 **Option 2: Heroku Deployment**

### **Step 1: Install Heroku CLI**

```bash
# Windows
winget install --id=Heroku.HerokuCLI

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### **Step 2: Login and Deploy**

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-brondby-tracker

# Add PostgreSQL database
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set NEWS_API_KEY=your_news_api_key
heroku config:set TELEGRAM_BOT_TOKEN=your_telegram_bot_token
heroku config:set TELEGRAM_CHAT_ID=your_telegram_chat_id
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Open your app
heroku open
```

---

## 🎯 **Option 3: Vercel Deployment (Dashboard Only)**

For a static dashboard version:

### **Step 1: Create Vercel Configuration**

Your `vercel.json` is already configured!

### **Step 2: Deploy to Vercel**

1. **Visit [Vercel.com](https://vercel.com)**
2. **Sign up with GitHub**
3. **Import your repository**
4. **Vercel will automatically deploy**

### **Step 3: Configure Environment Variables**

In Vercel dashboard → Settings → Environment Variables:

```env
NEWS_API_KEY=your_news_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

---

## 🎯 **Option 4: DigitalOcean App Platform**

### **Step 1: Create DigitalOcean Account**

1. **Visit [DigitalOcean.com](https://digitalocean.com)**
2. **Sign up and add payment method**
3. **Go to App Platform**

### **Step 2: Deploy**

1. **Click "Create App"**
2. **Connect your GitHub repository**
3. **Select Python as runtime**
4. **Configure environment variables**
5. **Deploy!**

---

## 🔧 **Post-Deployment Setup**

### **1. Set Up Database**

Your app will automatically create the database on first run.

### **2. Test Your API**

```bash
# Test your deployed API
curl https://your-app-url.railway.app/health
curl https://your-app-url.railway.app/stock/current
```

### **3. Set Up Scheduled Updates**

For Railway/Heroku, you can use:
- **Railway Cron Jobs** (built-in)
- **Heroku Scheduler** (addon)
- **External services** like Cron-job.org

### **4. Monitor Your App**

- **Railway**: Built-in monitoring
- **Heroku**: Heroku logs
- **Vercel**: Built-in analytics

---

## 🌐 **Custom Domain Setup**

### **Railway/Heroku**

1. **Buy domain** (Namecheap, GoDaddy, etc.)
2. **Add custom domain in platform dashboard**
3. **Update DNS records**

### **Vercel**

1. **Add custom domain in Vercel dashboard**
2. **Vercel will guide you through DNS setup**

---

## 🔒 **Security Considerations**

### **Environment Variables**
- ✅ Never commit API keys to Git
- ✅ Use platform environment variables
- ✅ Rotate keys regularly

### **HTTPS**
- ✅ All platforms provide HTTPS by default
- ✅ No additional setup needed

### **Rate Limiting**
- ✅ Consider adding rate limiting for production
- ✅ Monitor API usage

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
Your app includes health check endpoints:
- `GET /health` - Basic health check
- `GET /stock/current` - Stock data availability
- `GET /news/recent` - News data availability

### **Logs**
- **Railway**: `railway logs`
- **Heroku**: `heroku logs --tail`
- **Vercel**: Built-in log viewer

### **Performance**
- Monitor response times
- Set up alerts for downtime
- Track API usage

---

## 🚀 **Recommended Deployment Flow**

1. **Start with Railway** (easiest, most generous free tier)
2. **Test thoroughly** with your deployed app
3. **Set up monitoring** and alerts
4. **Add custom domain** when ready
5. **Scale up** as needed

---

## 🆘 **Troubleshooting**

### **Common Issues**

**App won't start:**
- Check environment variables
- Verify `requirements.txt` is complete
- Check logs for errors

**Database issues:**
- Ensure `DATABASE_URL` is set correctly
- Check database connection

**API keys not working:**
- Verify keys are correct
- Check API quotas
- Test keys locally first

### **Getting Help**

- **Railway**: Built-in support chat
- **Heroku**: Extensive documentation
- **Vercel**: Community forum
- **GitHub Issues**: For code-specific problems

---

## 🎉 **You're Live!**

Once deployed, your Brøndby IF Stock Tracker will be:
- ✅ Accessible from anywhere
- ✅ Running 24/7
- ✅ Automatically updated
- ✅ Monitored and secure

**Share your live dashboard with friends and fellow Brøndby fans!** 🏟️⚽📈
