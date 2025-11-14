#!/usr/bin/env python3
"""
Fix mislabeled categories in Rhone product data.
Uses product URLs and names to correctly categorize products.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def categorize_product(product):
    """
    Determine the correct category for a product based on URL and name.
    Returns the category name.
    """
    url = product.get('url', '').lower()
    name = product.get('name', '').lower()

    # Check URL path and product name for category indicators
    # Order matters - check more specific categories first

    # Accessories (bags, hats, socks, etc.)
    if any(x in url or x in name for x in [
        'accessories', 'beanie', 'hat', 'cap', 'sock', 'glove', 'belt',
        'bag', 'backpack', 'headband', 'wristband', 'towel', 'gift'
    ]):
        return 'Accessories'

    # Outerwear (jackets, hoodies, vests)
    if any(x in url or x in name for x in [
        'jacket', 'hoodie', 'vest', 'fleece', 'blazer', 'coat',
        'pullover', 'quarter-zip', 'half-zip', 'full-zip'
    ]):
        # Special case: if it also contains 'short' it might be a shirt
        if 'short' in name and 'sleeve' in name:
            return 'Tops'
        return 'Outerwear'

    # Sports Bras (women's specific)
    if any(x in url or x in name for x in ['bra', 'sports-bra', 'sportsbra']):
        return 'Sports Bras'

    # Leggings (women's specific)
    if 'legging' in url or 'legging' in name:
        return 'Leggings'

    # Shorts (before bottoms to catch them first)
    if 'short' in url or 'short' in name:
        # Make sure it's not "short sleeve"
        if 'sleeve' not in name:
            return 'Shorts'

    # Bottoms (pants, joggers, sweatpants)
    if any(x in url or x in name for x in [
        'pant', 'jogger', 'bottom', 'sweatpant', 'trouser',
        'commuter', 'chino', 'swift'
    ]):
        return 'Bottoms'

    # Tops (shirts, tees, tanks, polos)
    if any(x in url or x in name for x in [
        'shirt', 'tee', 't-shirt', 'tank', 'polo', 'top',
        'henley', 'crew', 'v-neck', 'sleeve', 'crewneck'
    ]):
        return 'Tops'

    # Default to Tops if we can't determine
    return 'Tops'


def fix_categories(input_file, output_file=None):
    """Fix categories in a JSON file"""
    print(f"Loading data from {input_file}...")

    with open(input_file, 'r') as f:
        products = json.load(f)

    if not isinstance(products, list):
        print("Error: Expected a list of products")
        return

    print(f"Loaded {len(products)} products")

    # Track category changes
    changes = {}
    unchanged = 0

    for product in products:
        old_category = product.get('category', 'Unknown')
        new_category = categorize_product(product)

        if old_category != new_category:
            if old_category not in changes:
                changes[old_category] = {}
            if new_category not in changes[old_category]:
                changes[old_category][new_category] = 0
            changes[old_category][new_category] += 1

            product['category'] = new_category
        else:
            unchanged += 1

    # Print summary
    print(f"\n📊 Category Changes:")
    if changes:
        for old_cat, new_cats in sorted(changes.items()):
            print(f"\n  {old_cat}:")
            for new_cat, count in sorted(new_cats.items()):
                print(f"    → {new_cat}: {count} products")
    else:
        print("  No changes needed!")

    print(f"\n  Unchanged: {unchanged} products")

    # Count final categories
    category_counts = {}
    for product in products:
        cat = product.get('category', 'Unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"\n📈 Final Category Distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} products")

    # Save output
    if output_file is None:
        output_file = input_file.replace('.json', '_fixed_categories.json')

    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"\n✅ Saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        # Find the most recent combined file
        data_dir = Path('data')
        json_files = sorted(data_dir.glob('rhone_products_combined_*.json'), reverse=True)

        if not json_files:
            print("No combined product files found in data/ directory")
            print("Usage: python fix_categories.py <path_to_json_file>")
            sys.exit(1)

        input_file = str(json_files[0])
        print(f"Using most recent combined file: {input_file}")
    else:
        input_file = sys.argv[1]

    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    fix_categories(input_file, output_file)


if __name__ == "__main__":
    main()
