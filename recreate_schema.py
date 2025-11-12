#!/usr/bin/env python3
"""
Recreate the Supabase schema by reading and executing schema.sql
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def recreate_schema():
    """Drop and recreate the products table"""
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        sys.exit(1)

    client = create_client(url, key)

    # Read schema file
    schema_file = Path(__file__).parent / "database" / "schema.sql"
    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    print("Recreating database schema...")
    print("This will delete all existing data!\n")

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    try:
        # Execute the schema
        # Note: Supabase doesn't support executing raw SQL through the Python client directly
        # You need to run this in the SQL editor on the Supabase dashboard
        print("\n" + "="*60)
        print("PLEASE RUN THE FOLLOWING SQL IN YOUR SUPABASE SQL EDITOR:")
        print("="*60)
        print(schema_sql)
        print("="*60)
        print("\nSteps:")
        print("1. Go to https://app.supabase.com")
        print("2. Open your project")
        print("3. Click 'SQL Editor' in the left sidebar")
        print("4. Copy the SQL above")
        print("5. Paste and click 'Run'")
        print("\nAfter running the SQL, you can upload your data:")
        print("  python3 database/upload_data.py data/rhone_products_combined_20251111_235837.json")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    recreate_schema()
