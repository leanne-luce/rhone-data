#!/usr/bin/env python3
"""
Update existing products in Supabase with color data from new scrape
"""

import json
import sys
sys.path.append('database')
from supabase_client import SupabaseClient

def update_colors():
    """Update products with new color data"""

    # Load new womens file with color data
    with open('data/data/rhone_products_collections_womens-view-all__1762923960714.json', 'r') as f:
        new_womens = json.load(f)

    print(f"Loaded {len(new_womens)} products with color data")

    # Create a mapping of image URL -> colors
    image_to_colors = {}
    for p in new_womens:
        imgs = p.get('images', [])
        colors = p.get('colors', [])
        if imgs and colors:
            img = imgs[0] if isinstance(imgs, list) else imgs
            image_to_colors[img] = colors

    print(f"Found {len(image_to_colors)} products with colors")

    # Get existing products from Supabase
    client = SupabaseClient()
    existing_products = client.get_all_products()

    print(f"Existing products in Supabase: {len(existing_products)}")

    # Find products that need color updates
    updates_needed = []
    for p in existing_products:
        imgs = p.get('images')
        if not imgs:
            continue

        # Get first image URL
        if isinstance(imgs, list) and len(imgs) > 0:
            img = imgs[0]
        elif isinstance(imgs, str):
            try:
                imgs_list = json.loads(imgs)
                img = imgs_list[0] if imgs_list else None
            except:
                img = imgs
        else:
            continue

        # Check if we have color data for this image
        if img in image_to_colors:
            new_colors = image_to_colors[img]
            existing_colors = p.get('colors', [])

            # Parse existing colors if it's a JSON string
            if isinstance(existing_colors, str):
                try:
                    existing_colors = json.loads(existing_colors)
                except:
                    existing_colors = []

            # Update if colors are different
            if set(new_colors) != set(existing_colors):
                updates_needed.append({
                    'id': p['id'],
                    'colors': new_colors,
                    'name': p.get('name', 'Unknown')
                })

    print(f"\nProducts needing color updates: {len(updates_needed)}")

    if not updates_needed:
        print("All products already have correct color data!")
        return

    # Update products
    print("\nUpdating products with new color data...")
    for i, update in enumerate(updates_needed):
        try:
            response = client.client.table('products').update({
                'colors': json.dumps(update['colors'])
            }).eq('id', update['id']).execute()

            if (i + 1) % 50 == 0:
                print(f"  Updated {i + 1}/{len(updates_needed)} products...")
        except Exception as e:
            print(f"  Error updating {update['name']}: {e}")

    print(f"\n✓ Updated {len(updates_needed)} products with color data!")

if __name__ == "__main__":
    update_colors()
