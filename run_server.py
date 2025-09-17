#!/usr/bin/env python3
"""
QuickBasket Production Server
Run the app using Waitress WSGI server for better performance and stability
"""

from waitress import serve
from app import app
import logging
import sys
import webbrowser
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def open_browser_delayed():
    """Open browser after server starts"""
    time.sleep(2)  # Wait for server to fully start
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    try:
        host = '0.0.0.0'  # Accept connections from any IP
        port = 5000
        
        print("=" * 60)
        print("🍽️  QuickBasket - Production Server Starting")
        print("=" * 60)
        print(f"Server: Waitress WSGI Server")
        print(f"Host: {host} (all interfaces)")
        print(f"Port: {port}")
        print(f"Local URL: http://127.0.0.1:{port}")
        print(f"Network URL: http://192.168.1.17:{port} (check your IP)")
        print("=" * 60)
        print("Features:")
        print("✅ Progressive Web App (PWA) - Installable on tablets")
        print("✅ Web scraping - Import recipes from any URL") 
        print("✅ Offline support - Service worker caching")
        print("✅ Production-grade WSGI server")
        print("=" * 60)
        
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the Waitress server
        logger.info(f"Starting Waitress WSGI server on {host}:{port}")
        serve(
            app,
            host=host,
            port=port,
            threads=6,  # Handle multiple concurrent requests
            connection_limit=1000,
            cleanup_interval=30,
            channel_timeout=120
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        print(f"\n❌ Failed to start server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)