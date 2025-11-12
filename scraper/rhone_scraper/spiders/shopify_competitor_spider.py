"""
Shopify Competitor Spider

A reusable spider for scraping product data from any Shopify store using the public Products JSON API.

Usage:
    scrapy crawl shopify_competitor -a stores="store1.com,store2.com,store3.com"
    scrapy crawl shopify_competitor -a stores="vuoriclothing.com" -a competitor_name="Vuori"

Features:
- Uses Shopify's public /products.json endpoint (no authentication needed)
- Handles cursor-based pagination automatically
- Respects rate limits with aggressive delays
- Works with any Shopify store
- Extracts comprehensive product data
"""

import scrapy
import json
from urllib.parse import urljoin, urlparse
import re


class ShopifyCompetitorSpider(scrapy.Spider):
    name = "shopify_competitor"

    # Custom settings for this spider
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # Shopify JSON API is public, robots.txt doesn't apply to API endpoints
        'DOWNLOAD_DELAY': 12,  # 12 second delay between requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Only 1 request at a time per store
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 20,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 86400,  # Cache for 24 hours
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Disable Playwright for this spider - we're just fetching JSON
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
            'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
        },
        # Add Accept header for JSON
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
    }

    def __init__(self, stores=None, competitor_name=None, *args, **kwargs):
        """
        Initialize spider with store URLs

        Args:
            stores: Comma-separated list of store domains (e.g., "store1.com,store2.com")
            competitor_name: Optional name for the competitor (used for all stores if only one provided)
        """
        super(ShopifyCompetitorSpider, self).__init__(*args, **kwargs)

        if not stores:
            raise ValueError("Please provide store URLs using -a stores='store1.com,store2.com'")

        # Parse store URLs
        self.stores = [store.strip() for store in stores.split(',')]
        self.competitor_name = competitor_name

        # Normalize URLs (ensure they have https://)
        self.start_urls = []
        for store in self.stores:
            if not store.startswith('http'):
                store = f'https://{store}'
            # Add /products.json endpoint with limit=250 (max allowed)
            products_url = urljoin(store, '/products.json?limit=250')
            self.start_urls.append(products_url)

        self.logger.info(f"Initialized Shopify spider for {len(self.start_urls)} stores")
        for url in self.start_urls:
            self.logger.info(f"  - {url}")

    def parse(self, response):
        """Parse products JSON response"""
        try:
            data = json.loads(response.text)
            products = data.get('products', [])

            # Extract store info from URL
            store_domain = urlparse(response.url).netloc

            self.logger.info(f"Processing {len(products)} products from {store_domain}")

            # Process each product
            for product in products:
                yield self.parse_product(product, store_domain)

            # Handle pagination using Link header
            # Shopify uses cursor-based pagination with page_info parameter
            link_header = response.headers.get('Link', b'').decode('utf-8')

            if link_header:
                # Parse Link header to find 'next' relation
                next_url = self.extract_next_page_url(link_header, response.url)
                if next_url:
                    self.logger.info(f"Following pagination to: {next_url}")
                    yield scrapy.Request(next_url, callback=self.parse)

            # Alternative: Check if we got the max limit (250), which suggests there might be more
            elif len(products) == 250:
                self.logger.warning(f"Got maximum products (250) from {store_domain} but no Link header. Pagination might be incomplete.")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from {response.url}: {e}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")

    def extract_next_page_url(self, link_header, current_url):
        """
        Extract next page URL from Link header

        Link header format: <https://store.com/products.json?page_info=xyz>; rel="next"
        """
        # Split by comma to get individual links
        links = link_header.split(',')

        for link in links:
            # Check if this is the 'next' link
            if 'rel="next"' in link or "rel='next'" in link:
                # Extract URL from <...>
                match = re.search(r'<([^>]+)>', link)
                if match:
                    next_url = match.group(1)
                    # Make sure it's absolute
                    return urljoin(current_url, next_url)

        return None

    def parse_product(self, product, store_domain):
        """
        Parse individual product from Shopify JSON

        Shopify product structure:
        {
            "id": 123456789,
            "title": "Product Name",
            "handle": "product-name",
            "body_html": "<p>Description</p>",
            "vendor": "Brand Name",
            "product_type": "Type",
            "tags": ["tag1", "tag2"],
            "variants": [...],
            "images": [...],
            "options": [...]
        }
        """

        # Determine competitor name
        competitor_name = self.competitor_name or product.get('vendor', store_domain)

        # Build product URL from handle
        product_url = f"https://{store_domain}/products/{product.get('handle', '')}"

        # Extract all available colors from variants
        colors = set()
        sizes = set()
        prices = []
        compare_prices = []

        for variant in product.get('variants', []):
            # Get price info
            if variant.get('price'):
                prices.append(float(variant['price']))
            if variant.get('compare_at_price'):
                compare_prices.append(float(variant['compare_at_price']))

            # Extract color and size from options
            # Shopify stores variant options like: option1, option2, option3
            # We need to match them with the product's options array
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

        # Clean HTML from description
        description = product.get('body_html', '')
        if description:
            # Remove HTML tags (basic cleaning)
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()

        # Determine gender from tags or product type
        gender = self.extract_gender(product)

        # Extract category from product_type or tags
        category = product.get('product_type') or 'Unknown'

        return {
            'product_id': str(product.get('id')),
            'name': product.get('title'),
            'url': product_url,
            'category': category,
            'subcategory': None,  # Shopify doesn't have subcategories by default
            'gender': gender,
            'price': price,
            'original_price': original_price,
            'sale_price': sale_price,
            'currency': 'USD',  # Default, could be extracted from variant if available
            'description': description[:1000] if description else None,  # Limit description length
            'colors': list(colors) if colors else [],
            'sizes': list(sizes) if sizes else [],
            'fabrics': [],  # Would need to extract from description or metafields
            'images': images,
            'is_best_seller': False,  # Not available in public API
            'best_seller_rank': None,
            'is_homepage_product': False,  # Not available in public API
            'competitor_name': competitor_name,
            'store_url': f"https://{store_domain}",
            'tags': product.get('tags', []),
            'vendor': product.get('vendor'),
        }

    def extract_gender(self, product):
        """
        Extract gender from product tags or type

        Common patterns: "mens", "womens", "unisex", "men's", "women's"
        """
        # Check tags first
        tags = [tag.lower() for tag in product.get('tags', [])]
        for tag in tags:
            if 'women' in tag or 'ladies' in tag or 'female' in tag:
                return 'Women'
            elif 'men' in tag and 'women' not in tag:  # Avoid "women" matching "men"
                return 'Men'
            elif 'unisex' in tag:
                return 'Unisex'

        # Check product type
        product_type = product.get('product_type', '').lower()
        if 'women' in product_type or 'ladies' in product_type:
            return 'Women'
        elif 'men' in product_type and 'women' not in product_type:
            return 'Men'

        # Check title as last resort
        title = product.get('title', '').lower()
        if 'women' in title or "women's" in title:
            return 'Women'
        elif 'men' in title or "men's" in title:
            return 'Men'

        return 'Unisex'  # Default if can't determine
