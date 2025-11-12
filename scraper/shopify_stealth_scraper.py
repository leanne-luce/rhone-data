#!/usr/bin/env python3
"""
Shopify Stealth Scraper using Playwright

Uses a real browser with stealth plugins to bypass bot detection.
This is more resource-intensive but has better success with aggressive protection.

Requirements:
    pip install playwright playwright-stealth
    playwright install chromium

Usage:
    python3 shopify_stealth_scraper.py "vuoriclothing.com" --output vuori.json
    python3 shopify_stealth_scraper.py "rhone.com" --output rhone.json --headless False
"""

import asyncio
import json
import argparse
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional

try:
    from playwright.async_api import async_playwright, Page
    from playwright_stealth import stealth_async
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("ERROR: playwright and playwright-stealth not installed!")
    print("Install with: pip install playwright playwright-stealth")
    print("Then run: playwright install chromium")
    exit(1)


class ShopifyStealthScraper:
    """Stealth scraper using real browser automation"""

    def __init__(self, delay: float = 5.0, headless: bool = True):
        """
        Initialize scraper

        Args:
            delay: Delay in seconds between requests (default 5)
            headless: Run browser in headless mode (default True)
        """
        self.delay = delay
        self.headless = headless

    async def fetch_products_page(self, page: Page, store_url: str, page_info: Optional[str] = None) -> Dict:
        """Fetch a single page of products"""

        # Normalize store URL
        if not store_url.startswith('http'):
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
            # Navigate to the JSON endpoint
            response = await page.goto(api_url, wait_until='networkidle', timeout=60000)

            if response.status != 200:
                print(f"  ✗ HTTP {response.status}")
                return {'products': [], 'next_page_info': None}

            # Get the page content
            content = await page.content()

            # Try to extract JSON from the page
            # Some sites wrap JSON in <pre> tags
            if '<pre' in content.lower():
                # Extract from pre tag
                import re
                match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL | re.IGNORECASE)
                if match:
                    json_text = match.group(1)
                else:
                    json_text = content
            else:
                json_text = content

            # Parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError:
                # Try getting it from the page's text content
                page_text = await page.inner_text('body')
                data = json.loads(page_text)

            products = data.get('products', [])

            # Check for pagination in response headers
            next_page_info = None
            headers = response.headers
            link_header = headers.get('link', '')
            if link_header:
                next_page_info = self._extract_next_page_info(link_header)

            print(f"  ✓ Found {len(products)} products")

            return {
                'products': products,
                'next_page_info': next_page_info
            }

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return {'products': [], 'next_page_info': None}

    def _extract_next_page_info(self, link_header: str) -> Optional[str]:
        """Extract page_info parameter from Link header"""
        links = link_header.split(',')
        for link in links:
            if 'rel="next"' in link or "rel='next'" in link:
                match = re.search(r'<([^>]+)>', link)
                if match:
                    url = match.group(1)
                    page_info_match = re.search(r'page_info=([^&]+)', url)
                    if page_info_match:
                        return page_info_match.group(1)
        return None

    async def scrape_store(self, store_url: str, competitor_name: Optional[str] = None, max_products: Optional[int] = None) -> List[Dict]:
        """Scrape all products from a store using browser automation"""

        print(f"\n{'='*60}")
        print(f"Scraping: {store_url}")
        print(f"Browser: {'Headless' if self.headless else 'Visible'}")
        print(f"{'='*60}")

        async with async_playwright() as p:
            # Launch browser with stealth mode
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Create context with realistic settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )

            page = await context.new_page()

            # Apply stealth mode
            await stealth_async(page)

            # Normalize URL
            if not store_url.startswith('http'):
                if not store_url.startswith('www.'):
                    store_url = f'https://www.{store_url}'
                else:
                    store_url = f'https://{store_url}'

            store_domain = urlparse(store_url).netloc
            all_products = []
            page_num = 1
            next_page_info = None

            # Optional: Visit homepage first to set cookies (more realistic)
            print(f"  Visiting homepage to establish session...")
            try:
                await page.goto(store_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)  # Pause like a human would
            except Exception as e:
                print(f"  Warning: Could not visit homepage: {e}")

            while True:
                # Fetch page
                result = await self.fetch_products_page(page, store_url, next_page_info)
                raw_products = result['products']

                if not raw_products:
                    break

                # Process products
                for product in raw_products:
                    processed = self.parse_product(product, store_domain, competitor_name)
                    all_products.append(processed)

                    if max_products and len(all_products) >= max_products:
                        print(f"\n  Reached max_products limit ({max_products})")
                        await browser.close()
                        return all_products

                # Check for next page
                next_page_info = result['next_page_info']
                if not next_page_info:
                    break

                page_num += 1
                print(f"  → Moving to page {page_num}...")

                # Human-like delay
                delay = self.delay + (asyncio.create_task(asyncio.sleep(0)).get_loop().time() % 2)  # Random variation
                await asyncio.sleep(delay)

            await browser.close()

            print(f"\n✓ Total products scraped: {len(all_products)}")
            return all_products

    def parse_product(self, product: Dict, store_domain: str, competitor_name: Optional[str] = None) -> Dict:
        """Parse Shopify product JSON into our schema"""

        comp_name = competitor_name or product.get('vendor', store_domain)
        product_url = f"https://{store_domain}/products/{product.get('handle', '')}"

        # Extract colors, sizes, prices from variants
        colors = set()
        sizes = set()
        prices = []
        compare_prices = []

        for variant in product.get('variants', []):
            if variant.get('price'):
                prices.append(float(variant['price']))
            if variant.get('compare_at_price'):
                compare_prices.append(float(variant['compare_at_price']))

            for i, option in enumerate(product.get('options', []), 1):
                option_name = option.get('name', '').lower()
                option_value = variant.get(f'option{i}')

                if option_value:
                    if 'color' in option_name or 'colour' in option_name:
                        colors.add(option_value)
                    elif 'size' in option_name:
                        sizes.add(option_value)

        price = min(prices) if prices else None
        original_price = min(compare_prices) if compare_prices else None
        sale_price = price if original_price and price < original_price else None

        images = [img.get('src') for img in product.get('images', []) if img.get('src')]

        description = product.get('body_html', '')
        if description:
            description = re.sub(r'<[^>]+>', '', description).strip()[:1000]

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
        tags = [tag.lower() for tag in product.get('tags', [])]
        for tag in tags:
            if 'women' in tag or 'ladies' in tag or 'female' in tag:
                return 'Women'
            elif 'men' in tag and 'women' not in tag:
                return 'Men'
            elif 'unisex' in tag:
                return 'Unisex'

        product_type = product.get('product_type', '').lower()
        if 'women' in product_type or 'ladies' in product_type:
            return 'Women'
        elif 'men' in product_type and 'women' not in product_type:
            return 'Men'

        title = product.get('title', '').lower()
        if 'women' in title or "women's" in title:
            return 'Women'
        elif 'men' in title or "men's" in title:
            return 'Men'

        return 'Unisex'


async def main():
    parser = argparse.ArgumentParser(description='Shopify Stealth Scraper using Browser Automation')
    parser.add_argument('stores', help='Comma-separated list of store domains')
    parser.add_argument('--name', '-n', help='Competitor name', default=None)
    parser.add_argument('--output', '-o', help='Output JSON file', default='shopify_products.json')
    parser.add_argument('--delay', '-d', type=float, default=5.0, help='Delay between requests (default: 5)')
    parser.add_argument('--max', '-m', type=int, help='Maximum products per store', default=None)
    parser.add_argument('--headless', type=lambda x: x.lower() != 'false', default=True,
                        help='Run browser in headless mode (default: True, use "False" to see browser)')

    args = parser.parse_args()

    stores = [s.strip() for s in args.stores.split(',')]
    scraper = ShopifyStealthScraper(delay=args.delay, headless=args.headless)

    all_products = []

    for store in stores:
        try:
            products = await scraper.scrape_store(store, competitor_name=args.name, max_products=args.max)
            all_products.extend(products)
        except Exception as e:
            print(f"\n✗ Error scraping {store}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print(f"Saving {len(all_products)} products to {args.output}")
    print(f"{'='*60}")

    with open(args.output, 'w') as f:
        json.dump(all_products, f, indent=2)

    print(f"✓ Done! Products saved to {args.output}")

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
    asyncio.run(main())
