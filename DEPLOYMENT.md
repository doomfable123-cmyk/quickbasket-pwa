# QuickBasket - Cloud Deployment Guide

## Free Cloud Hosting Options

### 1. **Render.com (Recommended - Free Tier)**

**Steps:**
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new "Web Service"
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3
   - **Instance Type**: Free

**Auto-deploy URL**: Your app will be at `https://your-app-name.onrender.com`

### 2. **Railway.app (Simple Setup)**

**Steps:**
1. Sign up at [railway.app](https://railway.app)
2. Connect GitHub and import repository  
3. Railway auto-detects Python and deploys
4. Set environment variables if needed

**Auto-deploy URL**: `https://your-app-name.up.railway.app`

### 3. **Heroku (Popular Choice)**

**Steps:**
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create account at [heroku.com](https://heroku.com)
3. Run commands:
```bash
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**Deploy URL**: `https://your-app-name.herokuapp.com`

### 4. **Fly.io (Modern Platform)**

**Steps:**
1. Install [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Run: `fly launch` (auto-generates config)
3. Deploy: `fly deploy`

## Quick Setup Instructions

1. **Create GitHub Repository** (if you haven't):
   - Go to github.com and create new repository
   - Upload your QuickBasket folder
   
2. **Choose Platform Above** and follow steps
   
3. **Your PWA will be available 24/7** at the provided URL

## Benefits of Cloud Hosting

✅ **No computer needed** - Runs independently  
✅ **Always accessible** - 24/7 availability  
✅ **HTTPS enabled** - Required for full PWA features  
✅ **Global access** - Use from anywhere  
✅ **Auto-scaling** - Handles traffic increases  

## Files Already Prepared

- `Procfile` - Tells hosting how to run your app
- `requirements.txt` - Lists all dependencies  
- Cloud detection in `app.py` - Optimized for hosting

## Recommended: Render.com

**Why Render:**
- Completely free tier
- Automatic HTTPS 
- Easy GitHub integration
- No credit card required
- Great for PWAs

**Render Setup Time:** ~5 minutes