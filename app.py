from flask import Flask, render_template
from supabase_client import supabase

app = Flask(__name__)

@app.route("/")
def home():
    # Test: fetch a table (create it first in Supabase dashboard)
    try:
        data = supabase.table("messages").select("*").execute()
        messages = data.data
    except Exception as e:
        messages = [{"error": str(e)}]

    return render_template("index.html", messages=messages)
