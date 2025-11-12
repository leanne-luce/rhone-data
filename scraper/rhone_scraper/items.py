import scrapy


class RhoneProductItem(scrapy.Item):
    """Item for storing Rhone product data"""

    # Basic product information
    product_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    gender = scrapy.Field()

    # Pricing
    price = scrapy.Field()
    sale_price = scrapy.Field()
    currency = scrapy.Field()

    # Product details
    description = scrapy.Field()
    colors = scrapy.Field()  # List of available colors
    sizes = scrapy.Field()  # List of available sizes
    fabrics = scrapy.Field()  # List of fabric materials

    # Ranking and popularity
    best_seller_rank = scrapy.Field()
    is_best_seller = scrapy.Field()

    # Images
    images = scrapy.Field()  # List of image URLs

    # Metadata
    scraped_at = scrapy.Field()
    is_homepage_product = scrapy.Field()

    # Additional fields
    sku = scrapy.Field()
    availability = scrapy.Field()
