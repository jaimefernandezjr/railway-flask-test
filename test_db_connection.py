#!/usr/bin/env python3
"""
Standalone database connection tester.
Run this independently: python test_db_connection.py
"""
import os
import sys
import time
import socket
from dotenv import load_dotenv

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)

# Load environment
print("\n[1] Loading environment variables...")
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ FAILED: Missing SUPABASE_URL or SUPABASE_KEY in .env")
    sys.exit(1)

print(f"✓ SUPABASE_URL: {url}")
print(f"✓ SUPABASE_KEY: {'***' + key[-10:]}")

# Test DNS resolution
print("\n[2] Testing DNS resolution...")
try:
    hostname = url.replace("https://", "").replace("http://", "").split("/")[0]
    print(f"   Hostname: {hostname}")
    ip = socket.gethostbyname(hostname)
    print(f"✓ DNS resolution SUCCESS: {hostname} -> {ip}")
except socket.gaierror as e:
    print(f"❌ DNS resolution FAILED: {e}")
    sys.exit(1)

# Test socket connection
print("\n[3] Testing socket connection on port 443...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((hostname, 443))
    sock.close()
    if result == 0:
        print(f"✓ Socket connection SUCCESS on port 443")
    else:
        print(f"❌ Socket connection FAILED on port 443 (error code: {result})")
        sys.exit(1)
except Exception as e:
    print(f"❌ Socket test FAILED: {e}")
    sys.exit(1)

# Test Supabase client creation
print("\n[4] Creating Supabase client...")
try:
    from supabase import create_client
    supabase = create_client(url, key)
    print(f"✓ Supabase client created successfully")
except Exception as e:
    print(f"❌ Supabase client creation FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

# Test simple query
print("\n[5] Testing database query (messages table)...")
max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"   Attempt {attempt + 1}/{max_retries}: Executing query...")
        start = time.time()
        response = supabase.table("messages").select("*").limit(1).execute()
        elapsed = time.time() - start
        print(f"✓ Query SUCCESS in {elapsed:.2f}s")
        print(f"   Response: {response}")
        break
    except socket.gaierror as e:
        print(f"   Attempt {attempt + 1} NETWORK ERROR: {e}")
        if attempt < max_retries - 1:
            wait = 2 ** attempt
            print(f"   Retrying in {wait} seconds...")
            time.sleep(wait)
        else:
            print(f"❌ Query FAILED after {max_retries} attempts")
            sys.exit(1)
    except Exception as e:
        print(f"   Attempt {attempt + 1} ERROR: {type(e).__name__}: {e}")
        if attempt < max_retries - 1:
            wait = 2 ** attempt
            print(f"   Retrying in {wait} seconds...")
            time.sleep(wait)
        else:
            print(f"❌ Query FAILED after {max_retries} attempts")
            sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Database connection is working!")
print("=" * 60)
