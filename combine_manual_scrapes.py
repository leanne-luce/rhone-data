#!/usr/bin/env python3
"""
Combine multiple manually scraped JSON files into one file.
"""

import json
import glob
from pathlib import Path
from datetime import datetime


def extract_category_from_filename(filename):
    """
    Extract category from filename.
    Examples:
      - rhone_products__collections_womens-view-all-accessories__*.json -> Accessories
      - rhone_products__collections_mens-view-all__*.json -> None (generic)
    """
    filename_lower = filename.lower()

    # Check for specific category keywords in filename
    if 'accessories' in filename_lower:
        return 'Accessories'
    elif 'outerwear' in filename_lower or 'jackets' in filename_lower:
        return 'Outerwear'
    elif 'shorts' in filename_lower:
        return 'Shorts'
    elif 'bottoms' in filename_lower or 'pants' in filename_lower:
        return 'Bottoms'
    elif 'tops' in filename_lower or 'shirts' in filename_lower:
        return 'Tops'
    elif 'leggings' in filename_lower:
        return 'Leggings'
    elif 'bras' in filename_lower or 'sports-bras' in filename_lower:
        return 'Sports Bras'

    return None  # No specific category found


def combine_manual_scrapes(input_dir="data"):
    """Combine multiple manually scraped JSON files"""

    # Find all JSON files in specified directory (Rhone, Vuori, Lululemon, Peter Millar, and Travis Mathew)
    json_files = glob.glob(f"{input_dir}/rhone_products_*.json") + \
                 glob.glob(f"{input_dir}/vuori-data/vuori_products_*.json") + \
                 glob.glob(f"{input_dir}/lululemon-data/lululemon_products_*.json") + \
                 glob.glob(f"{input_dir}/petermillar-data/petermillar_products_*.json") + \
                 glob.glob(f"{input_dir}/travismathew-data/travismathew_products_*.json")

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

        # Extract category from filename
        filename = Path(file_path).name
        file_category = extract_category_from_filename(filename)
        if file_category:
            print(f"  Category from filename: {file_category}")

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

                    # Set category from filename if available and not already set
                    if file_category and not product.get('category'):
                        product['category'] = file_category

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
                        # Prefer category from filename over inferred category
                        if file_category:
                            existing['category'] = file_category
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

        # Rename original_price to price (database schema uses 'price')
        if 'original_price' in product:
            product['price'] = product['original_price']
            del product['original_price']

        # Fix missing category - try to infer from product URL or name
        if not product.get('category') or product.get('category') == 'null' or product.get('category') == 'Other':
            url = product.get('url', '').lower()
            name = product.get('name', '').lower()

            # Try to determine category from URL or product name
            # Order matters - check more specific categories first

            # Accessories (bags, hats, socks, etc.)
            if any(x in url or x in name for x in ['accessories', 'beanie', 'hat', 'cap', 'sock', 'glove', 'belt', 'bag', 'backpack', 'headband', 'wristband', 'towel', 'gift', 'collar', 'cup', 'candle', 'paddle', 'bottle']):
                product['category'] = 'Accessories'
            # Outerwear (jackets, hoodies, vests) - check before tops
            elif any(x in url or x in name for x in ['jacket', 'hoodie', 'vest', 'fleece', 'blazer', 'coat', 'pullover', 'quarter-zip', 'half-zip', 'full-zip', 'puffer']):
                # Special case: if it also contains 'short' and 'sleeve' it might be a shirt
                if 'short' in name and 'sleeve' in name and 'jacket' not in name:
                    product['category'] = 'Tops'
                else:
                    product['category'] = 'Outerwear'
            # Sports Bras (women's specific)
            elif any(x in url or x in name for x in ['bra', 'sports-bra', 'sportsbra']):
                product['category'] = 'Sports Bras'
            # Leggings (women's specific)
            elif 'legging' in url or 'legging' in name:
                product['category'] = 'Leggings'
            # Shorts (before bottoms to catch them first)
            elif 'short' in url or ('short' in name and 'sleeve' not in name):
                product['category'] = 'Shorts'
            # Bottoms (pants, joggers, sweatpants)
            elif any(x in url or x in name for x in ['pant', 'jogger', 'bottom', 'sweatpant', 'trouser', 'commuter', 'chino', 'swift', 'tight']):
                product['category'] = 'Bottoms'
            # Tops (shirts, tees, tanks, polos)
            elif any(x in url or x in name for x in ['shirt', 'tee', 't-shirt', 'tank', 'polo', 'top', 'henley', 'crew', 'v-neck', 'sleeve', 'crewneck', 'mock-neck', 'sweater']):
                product['category'] = 'Tops'
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
