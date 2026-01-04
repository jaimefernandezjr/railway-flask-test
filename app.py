import sys
import time
import socket
from flask import Flask, render_template, jsonify
from supabase_client import supabase

print("[DEBUG] 1. Starting app.py initialization...", file=sys.stderr, flush=True)

app = Flask(__name__)
print("[DEBUG] 2. Flask app created", file=sys.stderr, flush=True)

def get_messages_with_retry(max_retries=3):
    """Fetch messages from Supabase with retry logic"""
    print("[DEBUG] 3. get_messages_with_retry() called", file=sys.stderr, flush=True)
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG]    Attempt {attempt + 1}/{max_retries}: Checking if supabase is available...", file=sys.stderr, flush=True)
            if supabase is None:
                print(f"[DEBUG]    Supabase is None, returning empty list", file=sys.stderr, flush=True)
                return []
            
            print(f"[DEBUG]    Supabase client is available, executing query...", file=sys.stderr, flush=True)
            print(f"[DEBUG]    Query: supabase.table('messages').select('*').execute()", file=sys.stderr, flush=True)
            
            start_time = time.time()
            data = supabase.table("messages").select("*").execute()
            elapsed = time.time() - start_time
            
            print(f"[DEBUG]    ✓ Query succeeded in {elapsed:.2f}s", file=sys.stderr, flush=True)
            print(f"[DEBUG]    Retrieved {len(data.data)} messages", file=sys.stderr, flush=True)
            return data.data
            
        except (socket.gaierror, OSError, ConnectionError, TimeoutError) as e:
            print(f"[DEBUG]    Attempt {attempt + 1} NETWORK ERROR - {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[DEBUG]    Retrying in {wait_time} seconds...", file=sys.stderr, flush=True)
                time.sleep(wait_time)
            else:
                print(f"[DEBUG]    ✗ Failed after {max_retries} attempts - returning empty list", file=sys.stderr, flush=True)
                return []
                
        except Exception as e:
            print(f"[DEBUG]    Attempt {attempt + 1} QUERY ERROR - {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[DEBUG]    Retrying in {wait_time} seconds...", file=sys.stderr, flush=True)
                time.sleep(wait_time)
            else:
                print(f"[DEBUG]    ✗ Failed after {max_retries} attempts - returning empty list", file=sys.stderr, flush=True)
                return []
    
    print(f"[DEBUG] 4. get_messages_with_retry() returning empty list", file=sys.stderr, flush=True)
    return []

@app.route("/")
def home():
    print("[DEBUG] HOME ROUTE CALLED", file=sys.stderr, flush=True)
    print("[DEBUG] 5. Calling get_messages_with_retry()...", file=sys.stderr, flush=True)
    messages = get_messages_with_retry()
    print(f"[DEBUG] 6. Got {len(messages)} messages", file=sys.stderr, flush=True)
    print("[DEBUG] 7. Rendering template with messages", file=sys.stderr, flush=True)
    return render_template("index.html", messages=messages)

@app.route("/health")
def health_check():
    """Health check endpoint - returns JSON status without HTML rendering"""
    print("[DEBUG] HEALTH CHECK ROUTE CALLED", file=sys.stderr, flush=True)
    
    status = {
        "status": "healthy",
        "supabase_client": supabase is not None,
        "timestamp": time.time()
    }
    
    if supabase is None:
        status["status"] = "degraded"
        status["message"] = "Supabase client not initialized"
        return jsonify(status), 503
    
    # Try to query the database
    try:
        print("[DEBUG] Health check: attempting query...", file=sys.stderr, flush=True)
        data = supabase.table("messages").select("*").limit(1).execute()
        status["database_connection"] = "ok"
        status["message"] = "Database connection successful"
        print("[DEBUG] Health check: query succeeded", file=sys.stderr, flush=True)
        return jsonify(status), 200
    except Exception as e:
        status["status"] = "degraded"
        status["database_connection"] = "failed"
        status["error"] = f"{type(e).__name__}: {str(e)}"
        status["message"] = "Database query failed"
        print(f"[DEBUG] Health check: query failed - {e}", file=sys.stderr, flush=True)
        return jsonify(status), 503
