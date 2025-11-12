#!/usr/bin/env python3
"""
Merge color data from new scrape files into existing database products
"""

import json
import sys
sys.path.append('database')
from supabase_client import SupabaseClient

def merge_colors(file_paths=None):
    """Merge colors from new files into existing products"""

    # Default files if none provided
    if file_paths is None:
        file_paths = [
            'data/data/rhone_products_collections_mens-view-all__1762924924668.json',
            'data/data/rhone_products_collections_womens-view-all__1762924930513.json',
            'data/data/rhone_products_collections_womens-view-all__1762925046818.json',
            'data/data/rhone_products_collections_womens-view-all__1762925060035.json',
            # Also try without nested data/ folder
            'data/rhone_products_collections_mens-view-all__1762924924668.json',
            'data/rhone_products_collections_womens-view-all__1762924930513.json',
            'data/rhone_products_collections_womens-view-all__1762925046818.json',
            'data/rhone_products_collections_womens-view-all__1762925060035.json',
        ]

    new_products = []

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                products = json.load(f)
                new_products.extend(products)
                print(f"✓ Loaded {len(products)} products from {file_path.split('/')[-1]}")
        except FileNotFoundError:
            continue  # Skip missing files silently

    if not new_products:
        print("No new products loaded!")
        return

    print(f"\nTotal new products loaded: {len(new_products)}")

    # Create a mapping of image URL -> colors
    image_to_colors = {}
    for p in new_products:
        imgs = p.get('images', [])
        colors = p.get('colors', [])
        if imgs and colors:
            img = imgs[0] if isinstance(imgs, list) else imgs
            image_to_colors[img] = colors

    print(f"Found {len(image_to_colors)} products with color data")

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

        # Check if we have NEW color data for this image
        if img in image_to_colors:
            new_colors = image_to_colors[img]
            existing_colors = p.get('colors', [])

            # Parse existing colors if it's a JSON string
            if isinstance(existing_colors, str):
                try:
                    existing_colors = json.loads(existing_colors)
                except:
                    existing_colors = []

            # Merge colors - combine old and new, remove duplicates
            merged_colors = list(set(existing_colors + new_colors))

            # Only update if there are new colors added
            if set(merged_colors) != set(existing_colors):
                updates_needed.append({
                    'id': p['id'],
                    'old_colors': existing_colors,
                    'new_colors': merged_colors,
                    'name': p.get('name', 'Unknown')
                })

    print(f"\nProducts needing color updates: {len(updates_needed)}")

    if not updates_needed:
        print("All products already have the latest color data!")
        return

    # Show sample updates
    print("\nSample updates:")
    for i, update in enumerate(updates_needed[:5]):
        print(f"\n{i+1}. {update['name']}")
        print(f"   Old colors ({len(update['old_colors'])}): {update['old_colors'][:3]}...")
        print(f"   New colors ({len(update['new_colors'])}): {update['new_colors'][:3]}...")

    # Update products
    print(f"\nUpdating {len(updates_needed)} products with merged color data...")
    for i, update in enumerate(updates_needed):
        try:
            response = client.client.table('products').update({
                'colors': json.dumps(update['new_colors'])
            }).eq('id', update['id']).execute()

            if (i + 1) % 50 == 0:
                print(f"  Updated {i + 1}/{len(updates_needed)} products...")
        except Exception as e:
            print(f"  Error updating {update['name']}: {e}")

    print(f"\n✓ Updated {len(updates_needed)} products with merged color data!")

if __name__ == "__main__":
    # Allow passing file paths as command line arguments
    if len(sys.argv) > 1:
        file_paths = sys.argv[1:]
        merge_colors(file_paths)
    else:
        merge_colors()
