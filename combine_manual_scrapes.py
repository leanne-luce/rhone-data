#!/usr/bin/env python3
"""
Combine multiple manually scraped JSON files into one file.
"""

import json
import glob
from pathlib import Path
from datetime import datetime


def combine_manual_scrapes():
    """Combine multiple manually scraped JSON files"""

    # Find all JSON files in data directory
    json_files = glob.glob("data/rhone_products_*.json")

    if not json_files:
        print("No JSON files found in data/ directory")
        print("Make sure to save your browser-extracted files there.")
        print("\nExample filenames:")
        print("  data/rhone_products_mens_tops.json")
        print("  data/rhone_products_womens_bottoms.json")
        return

    all_products = []
    seen_ids = set()

    for file_path in json_files:
        print(f"Reading {file_path}...")
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)

                # Handle both list and single object
                if isinstance(data, list):
                    products = data
                elif isinstance(data, dict):
                    products = [data]
                else:
                    print(f"  Skipping {file_path}: unexpected format")
                    continue

                for product in products:
                    product_id = product.get('product_id')
                    if product_id and product_id not in seen_ids:
                        # Ensure required fields exist
                        if 'scraped_at' not in product:
                            product['scraped_at'] = datetime.now().isoformat()

                        if 'currency' not in product:
                            product['currency'] = 'USD'

                        if 'colors' not in product:
                            product['colors'] = []

                        if 'sizes' not in product:
                            product['sizes'] = []

                        if 'fabrics' not in product:
                            product['fabrics'] = []

                        if 'images' not in product:
                            product['images'] = []

                        if 'is_best_seller' not in product:
                            product['is_best_seller'] = False

                        if 'availability' not in product:
                            product['availability'] = 'Unknown'

                        # Fix missing category - try to infer from product URL or name
                        if not product.get('category') or product.get('category') == 'null':
                            url = product.get('url', '').lower()
                            name = product.get('name', '').lower()

                            # Try to determine category from URL or product name
                            if any(x in url or x in name for x in ['pant', 'jogger', 'short', 'bottom']):
                                if 'short' in url or 'short' in name:
                                    product['category'] = 'Shorts'
                                else:
                                    product['category'] = 'Bottoms'
                            elif any(x in url or x in name for x in ['shirt', 'tee', 'tank', 'polo', 'top', 'henley', 'vneck', 'sleeve']):
                                product['category'] = 'Tops'
                            elif any(x in url or x in name for x in ['jacket', 'hoodie', 'vest', 'fleece', 'blazer', 'cardigan', 'sweater', 'pullover']):
                                product['category'] = 'Outerwear'
                            elif any(x in url or x in name for x in ['bra', 'sports-bra']):
                                product['category'] = 'Sports Bras'
                            elif 'legging' in url or 'legging' in name:
                                product['category'] = 'Leggings'
                            else:
                                product['category'] = 'Other'

                        all_products.append(product)
                        seen_ids.add(product_id)

            except json.JSONDecodeError as e:
                print(f"  Error reading {file_path}: {e}")
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")

    if not all_products:
        print("\nNo products found. Make sure your JSON files contain product data.")
        return

    print(f"\n✓ Combined {len(all_products)} unique products from {len(json_files)} files")

    # Save combined file
    output_file = f"data/rhone_products_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_products, f, indent=2)

    print(f"✓ Saved to: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Review the data: cat {output_file}")
    print(f"2. Upload to Supabase: python database/upload_data.py {output_file}")
    print(f"3. Launch dashboard: python run.py dashboard")


if __name__ == "__main__":
    combine_manual_scrapes()
