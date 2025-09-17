# 🍽️ QuickBasket PWA

A ### Browser Compatibility
- ✅ Chrome 80+
- ✅ Safari 11.1+
- ✅ Firefox 78+
- ✅ Edge 80+

### Windows Desktop App
For Windows users, a standalone executable is available:

1. **Download**: Get `QuickBasket.exe` from the [latest release](https://github.com/doomfable123-cmyk/quickbasket-pwa/blob/main/dist/QuickBasket.exe)
2. **Run**: Double-click the executable - no installation required!
3. **Features**: Full PWA functionality including offline support
4. **Size**: ~16MB standalone executable

The desktop app includes:
- 🖥️ **No Browser Required** - Runs as native Windows application
- 📱 **Same PWA Features** - All web app functionality in desktop form
- 🌐 **Recipe URL Scraping** - Import recipes from any cooking website
- 💾 **Local Database** - All data stored locally on your computer
- 🔄 **Automatic Updates** - Download new versions as released

#### 🔐 Security & Trust

To reduce Windows Defender warnings, you can digitally sign the executable:

1. **Quick Setup**: Double-click `Sign QuickBasket.bat` (requires Administrator privileges)
2. **Advanced Options**: See [CODE_SIGNING.md](CODE_SIGNING.md) for detailed instructions
3. **Commercial Certificates**: For wider distribution, consider purchasing a code signing certificate

**Note**: The unsigned version may show "Unknown Publisher" warnings - this is normal for new executables.essive Web App for smart recipe and grocery list management, optimized for tablets with web scraping capabilities.

## ✨ Features

- 📱 **Progressive Web App** - Install on any device like a native app
- 🌐 **Recipe Web Scraping** - Import recipes from any URL automatically
- ✏️ **Manual Recipe Entry** - Add your own recipes with custom ingredients and instructions  
- 🛒 **Smart Grocery Lists** - Generate shopping lists from selected recipes
- 💾 **Offline Support** - Works without internet connection via service worker
- 🖥️ **Cross-Platform** - Works on tablets, phones, and desktop browsers
- 🎨 **Modern UI** - Clean, responsive design with professional styling

## 🚀 Live Demo

The app is deployed and ready to use! Visit the live version and install it as a PWA on your device.

## 📱 Installation

### Install as PWA (Recommended)
1. Visit the app in your browser
2. Look for the install prompt at the top of the page
3. **Chrome/Edge**: Tap "Install Now" or look for install icon in address bar
4. **Safari (iPad)**: Tap Share → "Add to Home Screen"
5. **Android**: Use browser menu → "Add to Home screen"

### Browser Compatibility
- ✅ Chrome 80+
- ✅ Safari 11.1+
- ✅ Firefox 73+
- ✅ Edge 80+

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite
- **Web Scraping**: BeautifulSoup4 + requests
- **Server**: Waitress WSGI server (production-grade)
- **Frontend**: Vanilla JavaScript, Modern CSS
- **PWA**: Service Worker, Web App Manifest
- **Icons**: PIL/Pillow for PNG generation

## 🏗️ Local Development

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/quickbasket-pwa.git
   cd quickbasket-pwa
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux  
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open http://localhost:5000 in your browser

## 🚀 Deployment

This app is configured for easy deployment to various cloud platforms:

### Heroku
1. Create a Heroku app: `heroku create your-app-name`
2. Push to Heroku: `git push heroku main`

### Railway
1. Connect your GitHub repository to Railway
2. Deploy automatically on push

### Render
1. Connect your GitHub repository to Render
2. Deploy as a Web Service

### Environment Variables
The app automatically detects cloud environments and adjusts configuration accordingly.

## 📁 Project Structure

```
quickbasket-pwa/
├── app.py                 # Main Flask application
├── models.py              # Database models and setup
├── recipe_scraper.py      # Web scraping functionality  
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version specification
├── static/               # Static assets (CSS, JS, icons)
│   ├── manifest.json     # PWA manifest
│   ├── sw.js            # Service worker
│   └── *.png            # App icons
├── templates/           # HTML templates
│   ├── recipes.html     # Main recipes page
│   ├── add_recipe_*.html # Add recipe forms
│   ├── grocery_list.html # Grocery list view
│   └── pwa_debug.html   # PWA diagnostics
└── migrations/          # Database migrations
```

## 🐛 Debugging

Visit `/pwa-debug/` for comprehensive PWA diagnostics and troubleshooting tools.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

Made with ❤️ for home cooks and meal planners everywhere!