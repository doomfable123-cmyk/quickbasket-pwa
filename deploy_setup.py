#!/usr/bin/env python3
"""
QuickBasket Cloud Deployment Setup Script
Helps prepare your app for cloud hosting
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def check_git():
    """Check if git is installed and repository is initialized"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git is installed")
            
            # Check if this is a git repository
            if os.path.exists('.git'):
                print("✅ Git repository already initialized")
                return True
            else:
                print("❌ Not a git repository yet")
                return False
        else:
            print("❌ Git not found - please install Git first")
            return False
    except FileNotFoundError:
        print("❌ Git not installed - please install Git first")
        return False

def init_git():
    """Initialize git repository"""
    try:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit - QuickBasket PWA'], check=True)
        print("✅ Git repository initialized and files committed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing git: {e}")
        return False

def show_deployment_options():
    """Show cloud hosting options"""
    print_header("Cloud Hosting Options")
    
    options = [
        {
            "name": "Render.com",
            "difficulty": "⭐ Easiest",
            "price": "💚 Free",
            "time": "~5 minutes",
            "url": "https://render.com",
            "description": "Best for beginners, automatic HTTPS, no credit card needed"
        },
        {
            "name": "Railway.app", 
            "difficulty": "⭐ Easy",
            "price": "💚 Free tier", 
            "time": "~3 minutes",
            "url": "https://railway.app",
            "description": "Modern platform, simple GitHub integration"
        },
        {
            "name": "Heroku",
            "difficulty": "⭐⭐ Medium",
            "price": "💚 Free tier*",
            "time": "~10 minutes", 
            "url": "https://heroku.com",
            "description": "Popular choice, requires Heroku CLI installation"
        },
        {
            "name": "Fly.io",
            "difficulty": "⭐⭐ Medium",
            "price": "💚 Free allowance",
            "time": "~8 minutes",
            "url": "https://fly.io", 
            "description": "Modern, fast deployment"
        }
    ]
    
    for i, option in enumerate(options, 1):
        print(f"\n{i}. {option['name']}")
        print(f"   Difficulty: {option['difficulty']}")
        print(f"   Price: {option['price']}")
        print(f"   Setup Time: {option['time']}")
        print(f"   Description: {option['description']}")
        print(f"   URL: {option['url']}")

def show_render_instructions():
    """Show detailed Render.com setup instructions"""
    print_header("Render.com Setup Instructions (Recommended)")
    
    print("""
📱 STEP 1: Create GitHub Repository
1. Go to https://github.com and sign in (create account if needed)
2. Click "New repository" 
3. Name it "quickbasket-pwa"
4. Make it Public
5. Click "Create repository"

📱 STEP 2: Upload Your Code
1. On the new repository page, click "uploading an existing file"
2. Drag and drop all QuickBasket files from this folder
3. Write commit message: "Initial QuickBasket PWA"
4. Click "Commit changes"

📱 STEP 3: Deploy to Render
1. Go to https://render.com and sign up (use GitHub to sign in)
2. Click "New +" -> "Web Service"
3. Connect your GitHub account
4. Select your "quickbasket-pwa" repository
5. Use these settings:
   - Name: quickbasket-pwa (or your preferred name)
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
   - Instance Type: Free
6. Click "Create Web Service"

🎉 RESULT: Your app will be live at:
https://your-app-name.onrender.com

⏱️ Deploy Time: 3-5 minutes
💰 Cost: Completely FREE
🔒 HTTPS: Automatic
📱 PWA Ready: Yes!
    """)

def main():
    print_header("QuickBasket Cloud Deployment Setup")
    
    print("This script helps you deploy QuickBasket to the cloud so you can")
    print("use your PWA on any device without running a server on your computer!")
    
    # Check current directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the QuickBasket directory")
        sys.exit(1)
    
    print("✅ Found QuickBasket app files")
    
    # Check if deployment files exist
    files_needed = ['Procfile', 'requirements.txt', 'DEPLOYMENT.md']
    for file in files_needed:
        if os.path.exists(file):
            print(f"✅ {file} ready for deployment")
        else:
            print(f"❌ Missing {file}")
    
    print("\n" + "="*60)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. 📋 View all hosting options")
        print("2. 🚀 Get Render.com setup instructions (Recommended)")
        print("3. 🌐 Open GitHub to create repository")
        print("4. 🔧 Initialize Git repository (if needed)")
        print("5. 📖 Open deployment guide")
        print("6. ❌ Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            show_deployment_options()
        elif choice == '2':
            show_render_instructions()
            input("\nPress Enter to continue...")
        elif choice == '3':
            webbrowser.open('https://github.com/new')
            print("✅ Opening GitHub in your browser...")
        elif choice == '4':
            if not check_git():
                continue
            if not os.path.exists('.git'):
                if init_git():
                    print("✅ Git repository initialized successfully!")
                else:
                    print("❌ Failed to initialize git repository")
        elif choice == '5':
            if os.path.exists('DEPLOYMENT.md'):
                if sys.platform.startswith('win'):
                    os.startfile('DEPLOYMENT.md')
                else:
                    subprocess.run(['open', 'DEPLOYMENT.md'])
            else:
                print("❌ DEPLOYMENT.md not found")
        elif choice == '6':
            print("\n🎉 Ready to deploy QuickBasket to the cloud!")
            print("Your PWA will be accessible 24/7 from any device!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()