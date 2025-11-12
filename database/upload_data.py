#!/usr/bin/env python3
"""
Script to upload scraped product data to Supabase
"""

import json
import sys
from pathlib import Path
from supabase_client import SupabaseClient


def load_json_file(filepath: str) -> list:
    """Load product data from JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_products(json_file: str):
    """Upload products from JSON file to Supabase"""
    print(f"Loading data from {json_file}...")

    # Load products from file
    products = load_json_file(json_file)
    print(f"Loaded {len(products)} products")

    # Initialize Supabase client
    print("Connecting to Supabase...")
    client = SupabaseClient()

    # Upload products in batches
    batch_size = 100
    total_uploaded = 0

    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        print(f"Uploading batch {i // batch_size + 1} ({len(batch)} products)...")

        try:
            result = client.insert_products_batch(batch)
            total_uploaded += len(batch)
            print(f"Successfully uploaded {total_uploaded}/{len(products)} products")
        except Exception as e:
            print(f"Error uploading batch: {e}")
            # Continue with next batch
            continue

    print(f"\nUpload complete! Total products uploaded: {total_uploaded}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        # Find the most recent JSON file in data directory
        data_dir = Path(__file__).parent.parent / "data"
        json_files = sorted(data_dir.glob("rhone_products_*.json"), reverse=True)

        if not json_files:
            print("No product data files found in data/ directory")
            print("Usage: python upload_data.py <path_to_json_file>")
            sys.exit(1)

        json_file = str(json_files[0])
        print(f"Using most recent data file: {json_file}")
    else:
        json_file = sys.argv[1]

    upload_products(json_file)


if __name__ == "__main__":
    main()
