#!/usr/bin/env python3
"""
Combine multiple manually scraped JSON files into one file.
"""

import json
import glob
from pathlib import Path
from datetime import datetime


def combine_manual_scrapes(input_dir="data"):
    """Combine multiple manually scraped JSON files"""

    # Find all JSON files in specified directory
    json_files = glob.glob(f"{input_dir}/rhone_products_*.json")

    if not json_files:
        print(f"No JSON files found in {input_dir}/ directory")
        print("Make sure to save your browser-extracted files there.")
        print("\nExample filenames:")
        print("  data/rhone_products_mens_tops.json")
        print("  data/rhone_products_womens_bottoms.json")
        return

    # Use a dict to track products by URL (most specific) and merge duplicates
    products_by_url = {}

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
                    # Use URL as unique identifier (includes variant info)
                    url = product.get('url')
                    product_id = product.get('product_id')

                    if not url or not product_id:
                        continue

                    # Clean URL - remove query params like scrollTo
                    base_url = url.split('?')[0]
                    # Keep variant param if it exists
                    if '?variant=' in url:
                        variant_param = url.split('?variant=')[1].split('&')[0]
                        unique_url = f"{base_url}?variant={variant_param}"
                    else:
                        unique_url = base_url

                    # If we've seen this URL before, merge the data (keep most complete)
                    if unique_url in products_by_url:
                        existing = products_by_url[unique_url]
                        # Merge: keep non-empty values
                        for key, value in product.items():
                            if value and (not existing.get(key) or
                                         (isinstance(value, list) and len(value) > len(existing.get(key, []))) or
                                         (isinstance(value, str) and len(value) > len(str(existing.get(key, ''))))):
                                existing[key] = value
                        continue

                    # Add to our collection
                    products_by_url[unique_url] = product

            except json.JSONDecodeError as e:
                print(f"  Error reading {file_path}: {e}")
            except Exception as e:
                print(f"  Error processing {file_path}: {e}")

    if not products_by_url:
        print("\nNo products found. Make sure your JSON files contain product data.")
        return

    print(f"\n✓ Found {len(products_by_url)} unique products from {len(json_files)} files")

    # Convert dict to list and clean up each product
    all_products = []
    for product in products_by_url.values():
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

        # Ensure images is always an array
        if 'images' not in product:
            if 'image' in product and product['image']:
                product['images'] = [product['image']]
            else:
                product['images'] = []

        # Remove the single image field if it exists (database only has images array)
        if 'image' in product:
            del product['image']

        if 'is_best_seller' not in product:
            product['is_best_seller'] = False

        if 'availability' not in product:
            product['availability'] = 'Unknown'

        # Fix missing category - try to infer from product URL or name
        if not product.get('category') or product.get('category') == 'null' or product.get('category') == 'Other':
            url = product.get('url', '').lower()
            name = product.get('name', '').lower()

            # Try to determine category from URL or product name
            # Check outerwear first (more specific)
            if any(x in url or x in name for x in ['jacket', 'hoodie', 'vest', 'fleece', 'blazer', 'cardigan', 'sweater', 'pullover', 'zip', 'shacket']):
                product['category'] = 'Outerwear'
            # Accessories
            elif any(x in url or x in name for x in ['beanie', 'hat', 'cap', 'sock', 'glove', 'belt', 'bag', 'backpack', 'headband', 'wristband']):
                product['category'] = 'Accessories'
            # Bottoms
            elif any(x in url or x in name for x in ['trouser', 'pant', 'jogger', 'short', 'bottom', 'sweatpant']):
                if 'short' in url or 'short' in name:
                    product['category'] = 'Shorts'
                else:
                    product['category'] = 'Bottoms'
            # Tops
            elif any(x in url or x in name for x in ['shirt', 'tee', 'tank', 'polo', 'top', 'henley', 'vneck', 'sleeve', 'crewneck']):
                product['category'] = 'Tops'
            # Sports Bras
            elif any(x in url or x in name for x in ['bra', 'sports-bra']):
                product['category'] = 'Sports Bras'
            # Leggings
            elif 'legging' in url or 'legging' in name:
                product['category'] = 'Leggings'
            # Default to Tops if we can't determine
            else:
                product['category'] = 'Tops'

        # Fix gender detection
        url = product.get('url', '').lower()
        if 'womens' in url or '/women' in url:
            product['gender'] = 'Women'
        elif 'mens' in url or '/men' in url:
            product['gender'] = 'Men'

        all_products.append(product)

    print(f"✓ Processed {len(all_products)} products")

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
    import sys
    # Allow specifying input directory as argument
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    combine_manual_scrapes(input_dir)
