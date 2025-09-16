import sqlite3

conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, source_url FROM recipes ORDER BY id DESC LIMIT 3')
rows = cursor.fetchall()
print('Most recent recipes:')
for row in rows:
    url_text = row[2] if row[2] else "No URL"
    print(f'Recipe {row[0]}: {row[1]} - URL: {url_text}')
conn.close()