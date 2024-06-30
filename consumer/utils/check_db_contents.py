import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

def check_db_contents():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM website_analyses ORDER BY created_at DESC LIMIT 5")
        results = cur.fetchall()
        
        if not results:
            print("No results found in the database.")
        else:
            print("Latest 5 entries in the database:")
            for row in results:
                print(f"\nURL: {row['url']}")
                print(f"Analysis: {row['analysis'][:100]}...")  # Print first 100 chars of analysis
                print(f"Created at: {row['created_at']}")
                print("-" * 50)

    conn.close()

if __name__ == "__main__":
    check_db_contents()