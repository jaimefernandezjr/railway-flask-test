import os
import sys
import socket
import time
from supabase import create_client, Client
from dotenv import load_dotenv

print("[DEBUG] 1. Starting supabase_client.py initialization...", file=sys.stderr)

print("[DEBUG] 2. Loading environment variables from .env", file=sys.stderr)
load_dotenv()  # <- this loads variables from .env

print("[DEBUG] 3. Reading SUPABASE_URL", file=sys.stderr)
url: str = os.environ.get("SUPABASE_URL")
print(f"[DEBUG]    SUPABASE_URL = {url}", file=sys.stderr)

print("[DEBUG] 4. Reading SUPABASE_KEY", file=sys.stderr)
key: str = os.environ.get("SUPABASE_KEY")
print(f"[DEBUG]    SUPABASE_KEY = {'***' + key[-10:] if key else 'NOT FOUND'}", file=sys.stderr)

print("[DEBUG] 5. Setting socket timeout to 10 seconds", file=sys.stderr)
socket.setdefaulttimeout(10)

print("[DEBUG] 6. Attempting to create Supabase client...", file=sys.stderr)
supabase = None
max_retries = 5

for attempt in range(max_retries):
    try:
        print(f"[DEBUG]    Attempt {attempt + 1}/{max_retries}: Creating client...", file=sys.stderr)
        supabase: Client = create_client(url, key)
        print(f"[DEBUG] 7. ✓ SUCCESS: Supabase client created on attempt {attempt + 1}", file=sys.stderr)
        break
    except (socket.gaierror, ConnectionError, OSError, TimeoutError) as e:
        print(f"[DEBUG]    Attempt {attempt + 1} FAILED - {type(e).__name__}: {e}", file=sys.stderr)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"[DEBUG]    Waiting {wait_time} seconds before retry...", file=sys.stderr)
            time.sleep(wait_time)
        else:
            print(f"[DEBUG] 7. ✗ FAILED: All {max_retries} attempts exhausted", file=sys.stderr)
            supabase = None
    except Exception as e:
        print(f"[DEBUG]    Attempt {attempt + 1} FAILED - {type(e).__name__}: {e}", file=sys.stderr)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"[DEBUG]    Waiting {wait_time} seconds before retry...", file=sys.stderr)
            time.sleep(wait_time)
        else:
            print(f"[DEBUG] 7. ✗ FAILED: All {max_retries} attempts exhausted", file=sys.stderr)
            supabase = None

print(f"[DEBUG] 8. Supabase client final state: {supabase is not None}", file=sys.stderr)
