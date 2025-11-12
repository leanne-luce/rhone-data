#!/usr/bin/env python3
"""
Google Shopping Scraper for Competitor Analysis

Scrapes product data from Google Shopping search results.
This bypasses direct website scraping and uses publicly available Google data.

Requirements:
    pip install beautifulsoup4 requests

Usage:
    python3 google_shopping_scraper.py "Vuori mens joggers" --output vuori_joggers.json
    python3 google_shopping_scraper.py "Rhone commuter pants" --max 50
    python3 google_shopping_scraper.py "lululemon abc pants" --competitor "Lululemon"
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import argparse
from datetime import datetime
from urllib.parse import urlencode, quote_plus
import re
from typing import List, Dict, Optional


class GoogleShoppingScra per:
    """Scraper for Google Shopping results"""

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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_products(self, query: str, max_results: Optional[int] = None, competitor_name: Optional[str] = None) -> List[Dict]:
        """
        Search Google Shopping for products

        Args:
            query: Search query (e.g., "Vuori mens joggers", "Rhone commuter pants")
            max_results: Maximum number of results to return
            competitor_name: Name of the competitor brand

        Returns:
            List of product dictionaries
        """
        print(f"\n{'='*60}")
        print(f"Searching Google Shopping: '{query}'")
        print(f"{'='*60}")

        products = []
        start = 0
        page = 1

        while True:
            # Build Google Shopping search URL
            params = {
                'q': query,
                'tbm': 'shop',  # Shopping tab
                'start': start,
                'hl': 'en',
                'gl': 'us',
            }

            url = f"https://www.google.com/search?{urlencode(params)}"

            print(f"\n  Page {page}: Fetching results...")

            try:
                response = self.session.get(url, timeout=30)

                if response.status_code != 200:
                    print(f"  ✗ HTTP {response.status_code}")
                    break

                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find product cards - Google Shopping uses various selectors
                # Try multiple selectors as Google's HTML changes frequently
                product_cards = []

                # Method 1: Look for shopping results divs
                product_cards = soup.select('div[data-docid]')

                if not product_cards:
                    # Method 2: Look for product grid items
                    product_cards = soup.select('.sh-dgr__grid-result')

                if not product_cards:
                    # Method 3: Generic product container
                    product_cards = soup.select('div[data-pck]')

                if not product_cards:
                    print(f"  ✗ No products found on page {page}")
                    break

                print(f"  ✓ Found {len(product_cards)} products")

                # Parse each product card
                for card in product_cards:
                    product = self.parse_product_card(card, competitor_name)
                    if product:
                        products.append(product)

                        if max_results and len(products) >= max_results:
                            print(f"\n  Reached max_results limit ({max_results})")
                            return products

                # Check if there are more results
                # Look for "Next" link or pagination
                next_link = soup.select_one('a#pnnext')
                if not next_link:
                    print(f"\n  No more pages available")
                    break

                # Move to next page
                start += 10  # Google typically shows 10-20 results per page
                page += 1

                # Rate limiting
                print(f"  Waiting {self.delay} seconds before next page...")
                time.sleep(self.delay)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                break

        print(f"\n✓ Total products found: {len(products)}")
        return products

    def parse_product_card(self, card, competitor_name: Optional[str] = None) -> Optional[Dict]:
        """Parse a single product card from Google Shopping results"""

        try:
            # Extract product title
            title_elem = card.select_one('h3, h4, .tAxDx, [role="heading"]')
            title = title_elem.get_text(strip=True) if title_elem else None

            if not title:
                return None

            # Extract price
            price_elem = card.select_one('span[aria-label*="price"], .a8Pemb, b')
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self.extract_price(price_text) if price_text else None

            # Extract URL
            link_elem = card.select_one('a[href]')
            url = link_elem.get('href') if link_elem else None

            # Clean Google redirect URL
            if url and '/url?q=' in url:
                url = url.split('/url?q=')[1].split('&')[0]
            elif url and url.startswith('/'):
                url = f"https://www.google.com{url}"

            # Extract store/seller
            seller_elem = card.select_one('.aULzUe, .IuHnof, .merchant-name')
            seller = seller_elem.get_text(strip=True) if seller_elem else None

            # Extract image
            img_elem = card.select_one('img')
            image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None

            # Try to extract description
            desc_elem = card.select_one('.Ib8pOd, .product-description')
            description = desc_elem.get_text(strip=True) if desc_elem else None

            # Determine competitor name
            comp_name = competitor_name or seller or self.extract_brand_from_title(title)

            # Try to determine gender from title
            gender = self.extract_gender_from_text(title)

            # Try to determine category from title
            category = self.extract_category_from_text(title)

            # Extract color from title if present
            colors = self.extract_colors_from_text(title)

            return {
                'product_id': f"google_{abs(hash(url or title))}",
                'name': title,
                'url': url,
                'category': category,
                'subcategory': None,
                'gender': gender,
                'price': price,
                'original_price': None,
                'sale_price': None,
                'currency': 'USD',
                'description': description,
                'colors': colors,
                'sizes': [],
                'fabrics': [],
                'images': [image_url] if image_url else [],
                'is_best_seller': False,
                'best_seller_rank': None,
                'is_homepage_product': False,
                'competitor_name': comp_name,
                'store_url': seller,
                'tags': [],
                'vendor': seller,
                'scraped_at': datetime.utcnow().isoformat() + 'Z',
                'source': 'Google Shopping',
            }

        except Exception as e:
            print(f"  Warning: Error parsing product card: {e}")
            return None

    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from price text"""
        if not price_text:
            return None

        # Remove currency symbols and extract number
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except:
                return None
        return None

    def extract_brand_from_title(self, title: str) -> str:
        """Extract brand name from product title"""
        # Common brand patterns
        brands = ['Nike', 'Adidas', 'Lululemon', 'Vuori', 'Rhone', 'Gymshark',
                  'Under Armour', 'Patagonia', 'Arc\'teryx', 'Alo', 'Outdoor Voices']

        title_lower = title.lower()
        for brand in brands:
            if brand.lower() in title_lower:
                return brand

        # If no known brand, try to extract first word (often the brand)
        words = title.split()
        return words[0] if words else 'Unknown'

    def extract_gender_from_text(self, text: str) -> str:
        """Extract gender from text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['women', "women's", 'womens', 'ladies', 'female']):
            return 'Women'
        elif any(word in text_lower for word in ['men', "men's", 'mens', 'male']):
            return 'Men'
        elif 'unisex' in text_lower:
            return 'Unisex'

        return 'Unisex'

    def extract_category_from_text(self, text: str) -> str:
        """Extract category from product title"""
        text_lower = text.lower()

        # Category keywords
        categories = {
            'Tops': ['tee', 't-shirt', 'shirt', 'top', 'polo', 'hoodie', 'sweatshirt', 'tank'],
            'Bottoms': ['pants', 'joggers', 'shorts', 'leggings', 'tights', 'jeans'],
            'Outerwear': ['jacket', 'coat', 'vest', 'windbreaker', 'puffer'],
            'Accessories': ['hat', 'cap', 'bag', 'backpack', 'socks', 'gloves'],
            'Shoes': ['shoes', 'sneakers', 'trainers', 'runners'],
        }

        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return 'Unknown'

    def extract_colors_from_text(self, text: str) -> List[str]:
        """Extract colors from product title"""
        text_lower = text.lower()

        colors = ['black', 'white', 'grey', 'gray', 'blue', 'navy', 'red', 'green',
                  'yellow', 'orange', 'pink', 'purple', 'brown', 'beige', 'tan', 'olive']

        found_colors = []
        for color in colors:
            if color in text_lower:
                found_colors.append(color.capitalize())

        return found_colors


def main():
    parser = argparse.ArgumentParser(description='Google Shopping Scraper for Competitor Analysis')
    parser.add_argument('query', help='Search query (e.g., "Vuori mens joggers")')
    parser.add_argument('--competitor', '-c', help='Competitor brand name', default=None)
    parser.add_argument('--output', '-o', help='Output JSON file', default='google_shopping_products.json')
    parser.add_argument('--delay', '-d', type=float, default=3.0, help='Delay between pages (default: 3)')
    parser.add_argument('--max', '-m', type=int, help='Maximum products to scrape', default=None)

    args = parser.parse_args()

    scraper = GoogleShoppingScraper(delay=args.delay)
    products = scraper.search_products(args.query, max_results=args.max, competitor_name=args.competitor)

    if not products:
        print("\n✗ No products found!")
        return

    print(f"\n{'='*60}")
    print(f"Saving {len(products)} products to {args.output}")
    print(f"{'='*60}")

    with open(args.output, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"✓ Done! Products saved to {args.output}")

    # Print summary
    print(f"\nSummary:")
    print(f"  Total products: {len(products)}")

    if products:
        avg_price = sum(p['price'] for p in products if p['price']) / len([p for p in products if p['price']])
        print(f"  Average price: ${avg_price:.2f}")

        categories = {}
        for p in products:
            cat = p.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print(f"  Categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {cat}: {count}")


if __name__ == '__main__':
    main()
