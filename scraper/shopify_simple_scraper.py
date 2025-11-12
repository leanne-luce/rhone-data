#!/usr/bin/env python3
"""
Simple Shopify Product Scraper

A lightweight alternative to Scrapy for stores with strict bot protection.
Uses the requests library which has better success bypassing basic bot detection.

Usage:
    python shopify_simple_scraper.py vuoriclothing.com --output vuori_products.json
    python shopify_simple_scraper.py "gymshark.com,vuoriclothing.com,allbirds.com" --name "Competitors"
"""

import requests
import json
import time
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional


class ShopifySimpleScraper:
    """Simple scraper for Shopify stores using requests library"""

    def __init__(self, delay: float = 3.0):
        """
        Initialize scraper

        Args:
            delay: Delay in seconds between requests (default 3)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        })

    def fetch_products_page(self, store_url: str, page_info: Optional[str] = None) -> Dict:
        """
        Fetch a single page of products from Shopify store

        Args:
            store_url: Base URL of the store (e.g., "gymshark.com")
            page_info: Optional page_info parameter for pagination

        Returns:
            Dictionary with 'products' list and optional 'next_page_info'
        """
        # Normalize store URL
        if not store_url.startswith('http'):
            # Try both with and without www
            if not store_url.startswith('www.'):
                store_url = f'https://www.{store_url}'
            else:
                store_url = f'https://{store_url}'

        # Build API URL
        if page_info:
            api_url = f'{store_url}/products.json?limit=250&page_info={page_info}'
        else:
            api_url = f'{store_url}/products.json?limit=250'

        print(f"  Fetching: {api_url}")

        try:
            response = self.session.get(api_url, timeout=30, allow_redirects=True)

            # Check status code
            if response.status_code != 200:
                print(f"  ✗ HTTP {response.status_code}: {response.reason}")
                return {'products': [], 'next_page_info': None}

            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                print(f"  ✗ Unexpected content type: {content_type}")
                print(f"  Response preview: {response.text[:200]}")
                return {'products': [], 'next_page_info': None}

            data = response.json()
            products = data.get('products', [])

            # Check for pagination in Link header
            next_page_info = None
            link_header = response.headers.get('Link', '')
            if link_header:
                next_page_info = self._extract_next_page_info(link_header)

            print(f"  ✓ Found {len(products)} products")

            return {
                'products': products,
                'next_page_info': next_page_info
            }

        except requests.exceptions.JSONDecodeError as e:
            print(f"  ✗ JSON decode error: {e}")
            print(f"  Status: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"  Content preview: {response.text[:300] if 'response' in locals() else 'N/A'}")
            return {'products': [], 'next_page_info': None}
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request error: {e}")
            return {'products': [], 'next_page_info': None}

    def _extract_next_page_info(self, link_header: str) -> Optional[str]:
        """Extract page_info parameter from Link header"""
        # Look for rel="next" link
        links = link_header.split(',')
        for link in links:
            if 'rel="next"' in link or "rel='next'" in link:
                # Extract URL from <...>
                match = re.search(r'<([^>]+)>', link)
                if match:
                    url = match.group(1)
                    # Extract page_info parameter
                    page_info_match = re.search(r'page_info=([^&]+)', url)
                    if page_info_match:
                        return page_info_match.group(1)
        return None

    def scrape_store(self, store_url: str, competitor_name: Optional[str] = None, max_products: Optional[int] = None) -> List[Dict]:
        """
        Scrape all products from a Shopify store

        Args:
            store_url: Store domain or full URL
            competitor_name: Optional name for the competitor
            max_products: Optional limit on number of products to scrape

        Returns:
            List of processed product dictionaries
        """
        print(f"\n{'='*60}")
        print(f"Scraping: {store_url}")
        print(f"{'='*60}")

        # Normalize URL
        if not store_url.startswith('http'):
            # Try both with and without www
            if not store_url.startswith('www.'):
                store_url = f'https://www.{store_url}'
            else:
                store_url = f'https://{store_url}'

        store_domain = urlparse(store_url).netloc
        all_products = []
        page_num = 1
        next_page_info = None

        while True:
            # Fetch page
            result = self.fetch_products_page(store_url, next_page_info)
            raw_products = result['products']

            if not raw_products:
                break

            # Process products
            for product in raw_products:
                processed = self.parse_product(product, store_domain, competitor_name)
                all_products.append(processed)

                if max_products and len(all_products) >= max_products:
                    print(f"\n  Reached max_products limit ({max_products})")
                    return all_products

            # Check for next page
            next_page_info = result['next_page_info']
            if not next_page_info:
                break

            page_num += 1
            print(f"  → Moving to page {page_num}...")

            # Rate limiting
            time.sleep(self.delay)

        print(f"\n✓ Total products scraped: {len(all_products)}")
        return all_products

    def parse_product(self, product: Dict, store_domain: str, competitor_name: Optional[str] = None) -> Dict:
        """Parse Shopify product JSON into our schema"""

        # Determine competitor name
        comp_name = competitor_name or product.get('vendor', store_domain)

        # Build product URL
        product_url = f"https://{store_domain}/products/{product.get('handle', '')}"

        # Extract colors, sizes, prices from variants
        colors = set()
        sizes = set()
        prices = []
        compare_prices = []

        for variant in product.get('variants', []):
            # Prices
            if variant.get('price'):
                prices.append(float(variant['price']))
            if variant.get('compare_at_price'):
                compare_prices.append(float(variant['compare_at_price']))

            # Options (color, size)
            for i, option in enumerate(product.get('options', []), 1):
                option_name = option.get('name', '').lower()
                option_value = variant.get(f'option{i}')

                if option_value:
                    if 'color' in option_name or 'colour' in option_name:
                        colors.add(option_value)
                    elif 'size' in option_name:
                        sizes.add(option_value)

        # Calculate pricing
        price = min(prices) if prices else None
        original_price = min(compare_prices) if compare_prices else None
        sale_price = price if original_price and price < original_price else None

        # Extract images
        images = [img.get('src') for img in product.get('images', []) if img.get('src')]

        # Clean description
        description = product.get('body_html', '')
        if description:
            description = re.sub(r'<[^>]+>', '', description).strip()[:1000]

        # Extract gender
        gender = self.extract_gender(product)

        return {
            'product_id': str(product.get('id')),
            'name': product.get('title'),
            'url': product_url,
            'category': product.get('product_type') or 'Unknown',
            'subcategory': None,
            'gender': gender,
            'price': price,
            'original_price': original_price,
            'sale_price': sale_price,
            'currency': 'USD',
            'description': description,
            'colors': list(colors),
            'sizes': list(sizes),
            'fabrics': [],
            'images': images,
            'is_best_seller': False,
            'best_seller_rank': None,
            'is_homepage_product': False,
            'competitor_name': comp_name,
            'store_url': f"https://{store_domain}",
            'tags': product.get('tags', []),
            'vendor': product.get('vendor'),
            'scraped_at': datetime.utcnow().isoformat() + 'Z',
        }

    def extract_gender(self, product: Dict) -> str:
        """Extract gender from product tags, type, or title"""
        # Check tags
        tags = [tag.lower() for tag in product.get('tags', [])]
        for tag in tags:
            if 'women' in tag or 'ladies' in tag or 'female' in tag:
                return 'Women'
            elif 'men' in tag and 'women' not in tag:
                return 'Men'
            elif 'unisex' in tag:
                return 'Unisex'

        # Check product type
        product_type = product.get('product_type', '').lower()
        if 'women' in product_type or 'ladies' in product_type:
            return 'Women'
        elif 'men' in product_type and 'women' not in product_type:
            return 'Men'

        # Check title
        title = product.get('title', '').lower()
        if 'women' in title or "women's" in title:
            return 'Women'
        elif 'men' in title or "men's" in title:
            return 'Men'

        return 'Unisex'


def main():
    parser = argparse.ArgumentParser(description='Simple Shopify Product Scraper')
    parser.add_argument('stores', help='Comma-separated list of store domains (e.g., "gymshark.com,vuoriclothing.com")')
    parser.add_argument('--name', '-n', help='Competitor name (for single store)', default=None)
    parser.add_argument('--output', '-o', help='Output JSON file', default='shopify_products.json')
    parser.add_argument('--delay', '-d', type=float, default=3.0, help='Delay between requests in seconds (default: 3)')
    parser.add_argument('--max', '-m', type=int, help='Maximum products per store', default=None)

    args = parser.parse_args()

    # Parse stores
    stores = [s.strip() for s in args.stores.split(',')]

    # Initialize scraper
    scraper = ShopifySimpleScraper(delay=args.delay)

    all_products = []

    # Scrape each store
    for store in stores:
        try:
            products = scraper.scrape_store(store, competitor_name=args.name, max_products=args.max)
            all_products.extend(products)
        except Exception as e:
            print(f"\n✗ Error scraping {store}: {e}")
            continue

    # Save to file
    print(f"\n{'='*60}")
    print(f"Saving {len(all_products)} products to {args.output}")
    print(f"{'='*60}")

    with open(args.output, 'w') as f:
        json.dump(all_products, f, indent=2)

    print(f"✓ Done! Products saved to {args.output}")

    # Print summary
    if all_products:
        print(f"\nSummary:")
        print(f"  Total products: {len(all_products)}")

        competitors = {}
        for p in all_products:
            comp = p.get('competitor_name', 'Unknown')
            competitors[comp] = competitors.get(comp, 0) + 1

        print(f"  Stores:")
        for comp, count in competitors.items():
            print(f"    - {comp}: {count} products")


if __name__ == '__main__':
    main()
