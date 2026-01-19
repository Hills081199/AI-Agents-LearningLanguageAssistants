import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(url, key) if url and key else None

def get_supabase() -> Client:
    if not supabase:
        raise ValueError("Supabase is not configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")
    return supabase
