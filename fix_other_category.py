#!/usr/bin/env python3
"""
Fix products with 'Other' category by re-inferring their categories
"""

import json
import sys
sys.path.append('database')
from supabase_client import SupabaseClient

def infer_category(product):
    """Infer category from product URL and name"""
    url = product.get('url', '').lower()
    name = product.get('name', '').lower()

    # Check outerwear first (more specific)
    if any(x in url or x in name for x in ['jacket', 'hoodie', 'vest', 'fleece', 'blazer', 'cardigan', 'sweater', 'pullover', 'zip', 'shacket']):
        return 'Outerwear'
    # Accessories
    elif any(x in url or x in name for x in ['beanie', 'hat', 'cap', 'sock', 'glove', 'belt', 'bag', 'backpack', 'headband', 'wristband']):
        return 'Accessories'
    # Bottoms
    elif any(x in url or x in name for x in ['trouser', 'pant', 'jogger', 'short', 'bottom', 'sweatpant']):
        if 'short' in url or 'short' in name:
            return 'Shorts'
        else:
            return 'Bottoms'
    # Tops
    elif any(x in url or x in name for x in ['shirt', 'tee', 'tank', 'polo', 'top', 'henley', 'vneck', 'sleeve', 'crewneck']):
        return 'Tops'
    # Sports Bras
    elif any(x in url or x in name for x in ['bra', 'sports-bra']):
        return 'Sports Bras'
    # Leggings
    elif 'legging' in url or 'legging' in name:
        return 'Leggings'
    # Default to Tops if we can't determine
    else:
        return 'Tops'

def fix_other_category():
    """Fix products with 'Other' category"""

    client = SupabaseClient()
    products = client.get_all_products()

    print(f"Total products: {len(products)}")

    # Find products with 'Other' category
    other_products = [p for p in products if p.get('category') == 'Other']

    print(f"Products with 'Other' category: {len(other_products)}")

    if not other_products:
        print("No products with 'Other' category!")
        return

    # Infer new categories
    category_counts = {}
    updates = []

    for p in other_products:
        new_category = infer_category(p)

        updates.append({
            'id': p['id'],
            'category': new_category,
            'name': p.get('name', 'Unknown')
        })

        category_counts[new_category] = category_counts.get(new_category, 0) + 1

    print(f"\nNew category distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

    # Update products
    print(f"\nUpdating {len(updates)} products...")
    for i, update in enumerate(updates):
        try:
            response = client.client.table('products').update({
                'category': update['category']
            }).eq('id', update['id']).execute()

            if (i + 1) % 50 == 0:
                print(f"  Updated {i + 1}/{len(updates)} products...")
        except Exception as e:
            print(f"  Error updating {update['name']}: {e}")

    print(f"\n✓ Updated {len(updates)} products!")
    print("\nVerifying...")

    # Verify no more 'Other' category
    products = client.get_all_products()
    other_remaining = [p for p in products if p.get('category') == 'Other']
    print(f"Products still in 'Other' category: {len(other_remaining)}")

if __name__ == "__main__":
    fix_other_category()
