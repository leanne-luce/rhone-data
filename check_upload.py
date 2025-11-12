#!/usr/bin/env python3
"""
Check what was actually uploaded to Supabase and compare with local file
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "database"))

from database.supabase_client import SupabaseClient

def check_upload():
    print("Checking Supabase upload status...\n")

    # Load local file
    local_file = "data/rhone_products_combined_20251111_233730.json"
    with open(local_file, 'r') as f:
        local_products = json.load(f)

    print(f"📁 Local file: {len(local_products)} products")

    # Check Supabase
    try:
        client = SupabaseClient()
        db_products = client.get_all_products()
        print(f"☁️  Supabase: {len(db_products)} products")
        print(f"❌ Missing: {len(local_products) - len(db_products)} products\n")

        # Check which products are missing
        local_ids = {p['product_id'] for p in local_products}
        db_ids = {p['product_id'] for p in db_products}

        missing_ids = local_ids - db_ids

        if missing_ids:
            print(f"🔍 Found {len(missing_ids)} missing products")
            print("\nFirst 10 missing product IDs:")
            for i, pid in enumerate(list(missing_ids)[:10], 1):
                # Find the product in local data
                product = next((p for p in local_products if p['product_id'] == pid), None)
                if product:
                    print(f"  {i}. {pid} - {product.get('name', 'No name')}")

            # Check for common issues
            print("\n🔎 Analyzing missing products for common issues...")

            missing_products = [p for p in local_products if p['product_id'] in missing_ids]

            issues = {
                'no_name': 0,
                'no_price': 0,
                'no_category': 0,
                'no_url': 0
            }

            for p in missing_products:
                if not p.get('name'): issues['no_name'] += 1
                if not p.get('price'): issues['no_price'] += 1
                if not p.get('category'): issues['no_category'] += 1
                if not p.get('url'): issues['no_url'] += 1

            print("\nData quality issues in missing products:")
            print(f"  Missing name: {issues['no_name']}")
            print(f"  Missing price: {issues['no_price']}")
            print(f"  Missing category: {issues['no_category']}")
            print(f"  Missing URL: {issues['no_url']}")

        else:
            print("✅ All products uploaded successfully!")

        # Summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Local file:    {len(local_products)} products")
        print(f"Supabase DB:   {len(db_products)} products")
        print(f"Upload rate:   {len(db_products)/len(local_products)*100:.1f}%")

        if missing_ids:
            print(f"\n💡 Tip: Try re-running the upload:")
            print(f"   python database/upload_data.py {local_file}")

    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        print("\nMake sure:")
        print("1. .env file exists with correct credentials")
        print("2. Supabase project is active")
        print("3. Schema has been created")

if __name__ == "__main__":
    check_upload()
