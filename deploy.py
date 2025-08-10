#!/usr/bin/env python3
"""
Deployment Helper Script for Brøndby IF Stock Tracker
This script prepares your project for deployment
"""

import os
import shutil
import subprocess
import sys

def check_git_status():
    """Check if Git repository is clean"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  Warning: You have uncommitted changes!")
            print("Please commit your changes before deploying:")
            print(result.stdout)
            return False
        return True
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first.")
        return False

def create_gitignore():
    """Create .gitignore file if it doesn't exist"""
    gitignore_content = """
# Environment variables
.env
.env.local
.env.production

# Database files
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content.strip())
        print("✅ Created .gitignore file")
    else:
        print("✅ .gitignore already exists")

def check_requirements():
    """Check if requirements.txt exists and is complete"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ requirements.txt found")
    return True

def check_config_files():
    """Check if all necessary config files exist"""
    required_files = [
        'config.py',
        'config_production.py',
        'app.py',
        'Procfile',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All config files present")
    return True

def create_deployment_readme():
    """Create a deployment-specific README"""
    readme_content = """
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
"""
    
    with open('README_DEPLOYMENT.md', 'w', encoding='utf-8') as f:
        f.write(readme_content.strip())
    print("✅ Created deployment README")

def main():
    """Main deployment preparation function"""
    print("🚀 Brøndby IF Stock Tracker - Deployment Preparation")
    print("=" * 50)
    
    # Check Git status
    if not check_git_status():
        print("\n❌ Please commit your changes before deploying")
        return False
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure requirements.txt is complete")
        return False
    
    # Check config files
    if not check_config_files():
        print("\n❌ Please ensure all config files are present")
        return False
    
    # Create .gitignore
    create_gitignore()
    
    # Create deployment README
    create_deployment_readme()
    
    print("\n✅ Deployment preparation complete!")
    print("\n🎯 Next steps:")
    print("1. Commit all changes: git add . && git commit -m 'Prepare for deployment'")
    print("2. Push to GitHub: git push origin main")
    print("3. Choose your deployment platform (see DEPLOYMENT.md)")
    print("4. Set up environment variables")
    print("5. Deploy!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
