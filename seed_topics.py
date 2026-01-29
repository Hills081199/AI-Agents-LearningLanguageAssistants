import os
import sys
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

supabase = create_client(url, key)

topics = [
    {"name": "Greeting and Introduction", "level": "HSK 1", "language": "chinese"},
    {"name": "Family and Numbers", "level": "HSK 1", "language": "chinese"},
    {"name": "Date and Time", "level": "HSK 1", "language": "chinese"},
    {"name": "Ordering Food", "level": "HSK 2", "language": "chinese"},
    {"name": "Buying Tickets", "level": "HSK 2", "language": "chinese"},
    {"name": "Weather", "level": "HSK 2", "language": "chinese"},
    {"name": "Job Interview", "level": "HSK 3", "language": "chinese"},
    {"name": "Travel Plans", "level": "HSK 3", "language": "chinese"},
    {"name": "Seeing a Doctor", "level": "HSK 3", "language": "chinese"},
    {"name": "Online Shopping", "level": "HSK 4", "language": "chinese"},
    {"name": "Environmental Protection", "level": "HSK 4", "language": "chinese"},
    {"name": "Chinese Festivals", "level": "HSK 4", "language": "chinese"},
]

print(f"Seeding {len(topics)} topics...")

count = 0
for topic in topics:
    try:
        # Check if exists
        res = supabase.table("topics").select("id").eq("name", topic["name"]).eq("level", topic["level"]).execute()
        if not res.data:
            supabase.table("topics").insert(topic).execute()
            print(f"Added: {topic['name']}")
            count += 1
        else:
            print(f"Skipped (exists): {topic['name']}")
    except Exception as e:
        print(f"Error adding {topic['name']}: {e}")

print(f"Done. Added {count} new topics.")
