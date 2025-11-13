#!/usr/bin/env python3
"""
Clear existing products and upload new data.
Use with caution - this deletes all products!
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import sys

load_dotenv()

def clear_and_confirm():
    """Ask for confirmation before clearing data"""
    response = input("⚠️  This will DELETE ALL products from the database. Are you sure? (type 'yes' to confirm): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return False
    return True

def main():
    if not clear_and_confirm():
        return

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    # Count current products
    response = supabase.table('products').select('id', count='exact').execute()
    current_count = response.count
    print(f"\n🗑️  Deleting {current_count} existing products...")

    # Delete all products
    supabase.table('products').delete().neq('id', 0).execute()

    print(f"✅ Deleted {current_count} products")

    # Verify deletion
    response = supabase.table('products').select('id', count='exact').execute()
    print(f"📊 Remaining products: {response.count}")

    print("\n✅ Database cleared! Now run:")
    print("   python database/upload_data.py data/rhone_products_combined_20251112_211640.json")

if __name__ == "__main__":
    main()
