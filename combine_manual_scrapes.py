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
    seen_image_urls = set()

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
                    # Use image URL as unique identifier instead of product_id
                    # This treats each color variant as a separate product
                    images = product.get('images', [])
                    if not images:
                        continue

                    image_url = images[0] if isinstance(images, list) else images

                    # Skip if we've already seen this image
                    if image_url in seen_image_urls:
                        continue

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
                    seen_image_urls.add(image_url)

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
