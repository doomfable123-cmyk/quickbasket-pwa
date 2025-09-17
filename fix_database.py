#!/usr/bin/env python3
"""
Database Fix Script for QuickBasket PWA
Ensures the source_url column exists for saving recipe URLs.
Run this on your cloud deployment if recipes aren't saving URLs.
"""

import os
import sys
import sqlite3
from pathlib import Path

def fix_database_schema():
    """Ensure source_url column exists in recipes table."""
    print("🔧 Checking QuickBasket database schema...")
    
    # Find database file
    db_path = 'recipes.db'
    if not os.path.exists(db_path):
        print("❌ Database file 'recipes.db' not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(recipes);")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Current columns: {', '.join(columns)}")
        
        if 'source_url' not in columns:
            print("📝 Adding missing source_url column...")
            cursor.execute("ALTER TABLE recipes ADD COLUMN source_url VARCHAR(500);")
            conn.commit()
            print("✅ source_url column added successfully!")
        else:
            print("✅ source_url column already exists!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(recipes);")
        updated_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Updated columns: {', '.join(updated_columns)}")
        
        # Test with a simple query
        cursor.execute("SELECT COUNT(*) FROM recipes;")
        count = cursor.fetchone()[0]
        print(f"📊 Total recipes in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, title, source_url FROM recipes LIMIT 3;")
            sample_recipes = cursor.fetchall()
            print("🔍 Sample recipes:")
            for recipe in sample_recipes:
                url_status = "✅ Has URL" if recipe[2] else "❌ No URL"
                print(f"   - {recipe[1]}: {url_status}")
        
        conn.close()
        print("✅ Database schema fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🍽️  QuickBasket PWA - Database Fix")
    print("=" * 60)
    print("This script ensures recipe URLs are properly saved.")
    print("=" * 60)
    
    if fix_database_schema():
        print("\n🎉 Success! Your QuickBasket database is ready!")
        print("🌐 New recipes from URLs will now save the source URL.")
        print("💡 Restart your app to see the changes.")
    else:
        print("\n❌ Failed to fix database schema.")
        print("📧 Please check your database file and try again.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()