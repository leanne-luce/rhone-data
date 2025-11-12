#!/usr/bin/env python3
"""
Enrich product data by visiting product URLs to get detailed information.

WARNING: This script makes HTTP requests and may be blocked by Cloudflare.
Use it carefully with delays between requests.
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
    import requests
    from bs4 import BeautifulSoup


def enrich_products(input_file, delay=3):
    """
    Enrich product data by fetching details from product pages.

    Args:
        input_file: Path to JSON file with product URLs
        delay: Seconds to wait between requests (default: 3)
    """

    print(f"Loading products from {input_file}...")

    with open(input_file, 'r') as f:
        products = json.load(f)

    if not products:
        print("No products found in file.")
        return

    print(f"\nEnriching {len(products)} products...")
    print(f"Using {delay} second delay between requests")
    print("This will take a while. Press Ctrl+C to stop.\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    success_count = 0
    blocked_count = 0

    for i, product in enumerate(products):
        url = product.get('url')
        if not url:
            continue

        # Skip if already has detailed data
        if product.get('name') and product.get('description'):
            print(f"[{i+1}/{len(products)}] Skipping (already has data): {product.get('name')}")
            success_count += 1
            continue

        print(f"\n[{i+1}/{len(products)}] Fetching: {url}")

        try:
            # Respectful delay
            time.sleep(delay)

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 403:
                print(f"  ✗ Blocked by Cloudflare (403)")
                blocked_count += 1
                if blocked_count >= 3:
                    print("\n⚠️  Too many blocks. Cloudflare is blocking requests.")
                    print("You'll need to use the browser console method instead.")
                    break
                continue

            if response.status_code != 200:
                print(f"  ✗ Error: HTTP {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract product name
            if not product.get('name'):
                title = soup.find('h1', class_=lambda x: x and 'product' in x.lower() if x else False)
                if not title:
                    title = soup.find('h1')
                if title:
                    product['name'] = title.get_text(strip=True)

            # Extract description
            if not product.get('description'):
                desc = soup.find('div', class_=lambda x: x and 'description' in x.lower() if x else False)
                if desc:
                    product['description'] = desc.get_text(strip=True)[:500]

            # Extract price
            if not product.get('price'):
                price = soup.find(class_=lambda x: x and 'price' in x.lower() if x else False)
                if price:
                    price_text = price.get_text(strip=True)
                    # Try to extract number
                    import re
                    price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', price_text)
                    if price_match:
                        product['price'] = float(price_match.group(1))

            # Extract images
            if not product.get('images'):
                images = soup.find_all('img', class_=lambda x: x and 'product' in x.lower() if x else False)
                product['images'] = [img.get('src') for img in images if img.get('src')][:5]

            # Extract colors
            if not product.get('colors'):
                color_options = soup.find_all(class_=lambda x: x and 'color' in x.lower() if x else False)
                colors = []
                for opt in color_options:
                    color_text = opt.get_text(strip=True)
                    if color_text and len(color_text) < 30:
                        colors.append(color_text)
                product['colors'] = colors[:10]

            print(f"  ✓ Got: {product.get('name', 'Unknown')}")
            success_count += 1

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request error: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save enriched data
    output_file = input_file.replace('.json', '_enriched.json')
    if output_file == input_file:
        output_file = input_file.replace('.json', '') + '_enriched.json'

    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Successfully enriched: {success_count}/{len(products)}")
    print(f"  Blocked by Cloudflare: {blocked_count}")
    print(f"\nSaved enriched data to: {output_file}")
    print(f"\nNext step: python database/upload_data.py {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python enrich_product_data.py <json_file> [delay_seconds]")
        print("\nExample:")
        print("  python enrich_product_data.py data/rhone_products_combined.json 5")
        print("\nDelay is optional (default: 3 seconds)")
        sys.exit(1)

    input_file = sys.argv[1]
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    try:
        enrich_products(input_file, delay)
    except KeyboardInterrupt:
        print("\n\nStopped by user. Partial results may be saved.")


if __name__ == "__main__":
    main()
