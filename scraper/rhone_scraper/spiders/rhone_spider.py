import scrapy
from datetime import datetime
import re
import json
from rhone_scraper.items import RhoneProductItem


class RhoneSpider(scrapy.Spider):
    """Spider for scraping product data from rhone.com"""

    name = "rhone"
    allowed_domains = ["rhone.com"]
    start_urls = [
        "https://www.rhone.com/",
        "https://www.rhone.com/collections/mens-tops",
        "https://www.rhone.com/collections/mens-bottoms",
        "https://www.rhone.com/collections/mens-shorts",
        "https://www.rhone.com/collections/mens-outerwear",
        "https://www.rhone.com/collections/womens-tops",
        "https://www.rhone.com/collections/womens-bottoms",
        "https://www.rhone.com/collections/womens-outerwear",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.homepage_products = set()

    def parse(self, response):
        """Parse collection pages and homepage"""

        # Check if this is the homepage
        is_homepage = response.url == "https://www.rhone.com/"

        if is_homepage:
            # Extract products featured on homepage
            self.logger.info("Parsing homepage")
            product_links = response.css('a[href*="/products/"]::attr(href)').getall()
            for link in product_links:
                full_url = response.urljoin(link)
                self.homepage_products.add(full_url)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_product,
                    meta={"is_homepage_product": True}
                )
        else:
            # Parse collection page
            self.logger.info(f"Parsing collection page: {response.url}")

            # Extract all product links from the collection page
            product_links = response.css('a[href*="/products/"]::attr(href)').getall()

            for link in product_links:
                full_url = response.urljoin(link)
                # Skip if already seen on homepage
                is_homepage_product = full_url in self.homepage_products
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_product,
                    meta={"is_homepage_product": is_homepage_product}
                )

            # Follow pagination if exists
            next_page = response.css('a[rel="next"]::attr(href)').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response):
        """Parse individual product page"""

        item = RhoneProductItem()

        # Extract product ID from URL or data attributes
        product_id = self.extract_product_id(response)
        item["product_id"] = product_id

        # Basic information
        item["name"] = response.css("h1.product-title::text").get() or \
                       response.css("h1[class*='product']::text").get() or \
                       response.css("h1::text").get()

        item["url"] = response.url

        # Category and gender
        breadcrumbs = response.css("nav.breadcrumb a::text").getall()
        item["category"], item["subcategory"], item["gender"] = self.extract_category_info(response, breadcrumbs)

        # Pricing
        item["price"], item["sale_price"] = self.extract_pricing(response)
        item["currency"] = "USD"

        # Description
        item["description"] = " ".join(response.css("div.product-description *::text").getall()).strip() or \
                             " ".join(response.css("div[class*='description'] *::text").getall()).strip()

        # Colors - extract from color swatches or options
        colors = self.extract_colors(response)
        item["colors"] = colors

        # Sizes
        sizes = response.css("select[name='Size'] option::text").getall() or \
                response.css("input[name='Size']::attr(value)").getall() or \
                response.css("button[data-size]::attr(data-size)").getall()
        item["sizes"] = [s.strip() for s in sizes if s.strip() and s.strip().lower() != "select size"]

        # Fabrics - extract from product description or details
        fabrics = self.extract_fabrics(response)
        item["fabrics"] = fabrics

        # Best seller information
        item["is_best_seller"] = bool(response.css(".badge--best-seller, [class*='bestseller']").get())
        item["best_seller_rank"] = None  # Will need to be determined from collection page order

        # Images
        images = response.css("img[class*='product']::attr(src)").getall() or \
                 response.css("div.product-images img::attr(src)").getall()
        item["images"] = [response.urljoin(img) for img in images if img]

        # Metadata
        item["scraped_at"] = datetime.now().isoformat()
        item["is_homepage_product"] = response.meta.get("is_homepage_product", False)

        # SKU and availability
        item["sku"] = response.css("[data-sku]::attr(data-sku)").get() or product_id
        item["availability"] = self.extract_availability(response)

        self.logger.info(f"Scraped product: {item.get('name', 'Unknown')}")

        yield item

    def extract_product_id(self, response):
        """Extract product ID from page"""
        # Try multiple methods
        product_id = response.css("[data-product-id]::attr(data-product-id)").get()

        if not product_id:
            # Extract from URL
            match = re.search(r'/products/([^/?]+)', response.url)
            if match:
                product_id = match.group(1)

        return product_id

    def extract_category_info(self, response, breadcrumbs):
        """Extract category, subcategory, and gender from breadcrumbs or URL"""
        category = None
        subcategory = None
        gender = None

        # Try to determine from URL
        url_lower = response.url.lower()
        if "mens" in url_lower or "/men" in url_lower:
            gender = "Men"
        elif "womens" in url_lower or "/women" in url_lower:
            gender = "Women"

        # Extract from breadcrumbs
        if len(breadcrumbs) > 1:
            category = breadcrumbs[1] if len(breadcrumbs) > 1 else None
            subcategory = breadcrumbs[2] if len(breadcrumbs) > 2 else None

        # Try to extract from collection info
        if not category:
            category = response.css("span.collection-title::text").get()

        return category, subcategory, gender

    def extract_pricing(self, response):
        """Extract regular and sale pricing"""
        price = None
        sale_price = None

        # Try multiple selectors for price
        price_text = response.css("span.price::text, .product-price::text, [class*='price']::text").get()

        if price_text:
            # Extract numbers from price text
            price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', price_text)
            if price_match:
                price = float(price_match.group(1))

        # Check for sale price
        sale_text = response.css("span.sale-price::text, .compare-at-price::text").get()
        if sale_text:
            sale_match = re.search(r'\$?(\d+(?:\.\d{2})?)', sale_text)
            if sale_match:
                sale_price = float(sale_match.group(1))

        return price, sale_price

    def extract_colors(self, response):
        """Extract available colors"""
        colors = []

        # Try color swatches
        color_names = response.css("input[name='Color']::attr(value)").getall() or \
                     response.css("button[data-color]::attr(data-color)").getall() or \
                     response.css("select[name='Color'] option::text").getall()

        colors = [c.strip() for c in color_names if c.strip() and c.strip().lower() != "select color"]

        # If no colors found, try to extract from title or description
        if not colors:
            color_pattern = r'\b(black|white|blue|red|green|navy|grey|gray|charcoal|heather|tan|khaki|olive|burgundy)\b'
            title = response.css("h1::text").get() or ""
            matches = re.findall(color_pattern, title.lower())
            colors = list(set(matches))

        return colors

    def extract_fabrics(self, response):
        """Extract fabric information from product description"""
        fabrics = []

        # Common fabric keywords
        fabric_keywords = [
            "cotton", "polyester", "nylon", "spandex", "elastane", "rayon",
            "modal", "bamboo", "wool", "merino", "cashmere", "silk",
            "linen", "acrylic", "fleece", "jersey"
        ]

        # Get all text from product description and details
        all_text = " ".join(response.css("div.product-description *::text, div.product-details *::text").getall()).lower()

        # Search for fabric keywords
        for fabric in fabric_keywords:
            if fabric in all_text:
                fabrics.append(fabric.capitalize())

        # Try to extract percentage information
        fabric_percentages = re.findall(r'(\d+%?\s*(?:' + '|'.join(fabric_keywords) + r'))', all_text, re.IGNORECASE)
        if fabric_percentages:
            fabrics = list(set(fabric_percentages))

        return list(set(fabrics))

    def extract_availability(self, response):
        """Check if product is available"""
        # Check for out of stock indicators
        out_of_stock = response.css(".sold-out, .out-of-stock, [class*='unavailable']").get()

        if out_of_stock:
            return "Out of Stock"

        # Check if add to cart button exists
        add_to_cart = response.css("button[type='submit'][name='add'], button.add-to-cart").get()

        if add_to_cart:
            return "In Stock"

        return "Unknown"
