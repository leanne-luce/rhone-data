#!/usr/bin/env python3
"""
Clear existing products and upload new data (no confirmation).
"""

import os
import sys
from pathlib import Path
from supabase_client import SupabaseClient
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        # Find the most recent JSON file
        data_dir = Path(__file__).parent.parent / "data"
        json_files = sorted(data_dir.glob("*_fixed_categories.json"), reverse=True)

        if not json_files:
            json_files = sorted(data_dir.glob("rhone_products_combined_*.json"), reverse=True)

        if not json_files:
            print("No product data files found in data/ directory")
            print("Usage: python clear_and_upload_auto.py <path_to_json_file>")
            sys.exit(1)

        json_file = str(json_files[0])
        print(f"Using most recent data file: {json_file}")
    else:
        json_file = sys.argv[1]

    # Initialize client
    print("Connecting to Supabase...")
    client = SupabaseClient()

    # Count current products
    current_count = client.get_product_count()
    print(f"\n🗑️  Deleting {current_count} existing products...")

    # Delete all products
    client.delete_all_products()
    print(f"✅ Deleted {current_count} products")

    # Verify deletion
    remaining = client.get_product_count()
    print(f"📊 Remaining products: {remaining}")

    # Upload new data
    print(f"\n📤 Uploading new data from {json_file}...")

    import json
    with open(json_file, 'r') as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products")

    # Upload in batches
    batch_size = 100
    total_uploaded = 0

    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        print(f"Uploading batch {i // batch_size + 1} ({len(batch)} products)...")

        try:
            result = client.insert_products_batch(batch)
            if result:
                total_uploaded += len(batch)
            print(f"Successfully uploaded {total_uploaded}/{len(products)} products")
        except Exception as e:
            print(f"Error uploading batch: {e}")
            continue

    print(f"\n✅ Upload complete! Total products uploaded: {total_uploaded}")

    # Final count
    final_count = client.get_product_count()
    print(f"📊 Final product count in database: {final_count}")


if __name__ == "__main__":
    main()
