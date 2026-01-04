from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Insert test data
data = supabase.table("messages").insert({
    "content": "Hello from Flask!"
}).execute()

print(f"Inserted: {data}")

# Query back
messages = supabase.table("messages").select("*").execute()
print(f"Messages in DB: {messages}")