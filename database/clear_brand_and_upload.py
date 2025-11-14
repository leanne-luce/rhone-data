#!/usr/bin/env python3
"""
Clear products for a specific brand and upload new data.
"""

import os
import sys
import json
from pathlib import Path
from supabase_client import SupabaseClient
from dotenv import load_dotenv

load_dotenv()

def delete_brand_products(client: SupabaseClient, brand: str) -> int:
    """Delete all products for a specific brand"""
    # Get count first
    response = client.client.table("products").select("id", count="exact").eq("brand", brand).execute()
    count = response.count

    # Delete all products for this brand
    client.client.table("products").delete().eq("brand", brand).execute()

    return count

def main():
    if len(sys.argv) < 2:
        print("Usage: python clear_brand_and_upload.py <path_to_json_file> [brand_name]")
        print("Example: python clear_brand_and_upload.py data/rhone_products_combined_*.json Vuori")
        sys.exit(1)

    json_file = sys.argv[1]

    # If brand not specified, try to detect from file
    if len(sys.argv) >= 3:
        brand = sys.argv[2]
    else:
        # Try to detect brand from file content
        with open(json_file, 'r') as f:
            products = json.load(f)

        if products and len(products) > 0:
            brand = products[0].get('brand', 'Unknown')
        else:
            print("Could not detect brand from file. Please specify brand as second argument.")
            sys.exit(1)

    print(f"Brand: {brand}")

    # Initialize client
    print("Connecting to Supabase...")
    client = SupabaseClient()

    # Delete brand products
    deleted_count = delete_brand_products(client, brand)
    print(f"\n🗑️  Deleted {deleted_count} existing {brand} products")

    # Upload new data
    print(f"\n📤 Uploading new {brand} data from {json_file}...")

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
                total_uploaded += len(result)
            print(f"Successfully uploaded {total_uploaded}/{len(products)} products")
        except Exception as e:
            print(f"Error uploading batch: {e}")
            continue

    print(f"\n✅ Upload complete! Total {brand} products uploaded: {total_uploaded}")

    # Final count for this brand
    final_response = client.client.table("products").select("id", count="exact").eq("brand", brand).execute()
    final_count = final_response.count
    print(f"📊 Final {brand} product count in database: {final_count}")


if __name__ == "__main__":
    main()
