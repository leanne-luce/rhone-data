#!/usr/bin/env python3
"""
Fix Vuori product names by extracting from product_id
"""

import json
import sys

def product_id_to_name(product_id):
    """Convert product ID to readable product name"""
    if not product_id:
        return None

    # Remove trailing slash
    name = product_id.rstrip('/')

    # Replace hyphens with spaces
    name = name.replace('-', ' ')

    # Title case each word
    name = ' '.join(word.capitalize() for word in name.split())

    # Remove size info at the end (e.g., "28", "30")
    words = name.split()
    if words and words[-1].isdigit() and len(words[-1]) <= 2:
        words = words[:-1]
        name = ' '.join(words)

    return name


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_vuori_names.py <json_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace('.json', '_fixed.json')

    print(f"Reading {input_file}...")
    with open(input_file, 'r') as f:
        products = json.load(f)

    print(f"Processing {len(products)} products...")

    fixed_count = 0
    for product in products:
        # Only fix Vuori products without names
        if product.get('brand') == 'Vuori' and not product.get('name'):
            product_id = product.get('product_id')
            if product_id:
                name = product_id_to_name(product_id)
                if name:
                    product['name'] = name
                    fixed_count += 1

    print(f"Fixed {fixed_count} Vuori product names")

    print(f"Writing to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"✓ Done! Saved to {output_file}")
    print(f"\nNext step: python database/clear_brand_and_upload.py {output_file} Vuori")


if __name__ == "__main__":
    main()
