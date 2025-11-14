#!/usr/bin/env python3
"""
Extract product names from URLs/product_ids for Vuori products.
"""

import json
import sys
from datetime import datetime

def product_id_to_name(product_id):
    """Convert product ID to readable name"""
    # Remove trailing slash
    name = product_id.rstrip('/')

    # Remove gender prefix (womens-, mens-)
    name = name.replace('womens-', '').replace('mens-', '')

    # Replace hyphens with spaces
    name = name.replace('-', ' ')

    # Capitalize each word
    name = ' '.join(word.capitalize() for word in name.split())

    return name

def fix_names(input_file):
    """Add names to products based on product_id"""
    with open(input_file, 'r') as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products")

    fixed_count = 0
    for product in products:
        if not product.get('name') and product.get('product_id'):
            product['name'] = product_id_to_name(product['product_id'])
            fixed_count += 1

    print(f"Fixed {fixed_count} product names")

    # Save to new file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = input_file.replace('.json', f'_fixed_names.json')

    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"Saved to: {output_file}")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_vuori_names.py <json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = fix_names(input_file)

    print(f"\nNext step:")
    print(f"python database/clear_brand_and_upload.py {output_file} Vuori")
