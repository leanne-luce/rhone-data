# Shopify Competitor Scraper Guide

This guide explains how to scrape product data from Shopify-based competitor stores for competitive analysis.

## Overview

This project includes **two approaches** for scraping Shopify stores:

1. **Simple Python Script** (`shopify_simple_scraper.py`) - Recommended
   - Uses requests library
   - Easier to use
   - Better success rate with bot protection
   - No heavy dependencies

2. **Scrapy Spider** (`shopify_competitor_spider.py`) - Advanced
   - More powerful for large-scale scraping
   - Better for automation
   - May be blocked by aggressive bot protection

## Prerequisites

### Required Dependencies

The simple scraper requires Python 3.8+ with the following packages:

```bash
python3 -m pip install requests brotli
```

**Important:** The `brotli` or `brotlicffi` package is required to decompress Brotli-encoded responses from Shopify stores.

For the Scrapy approach, you'll also need:

```bash
python3 -m pip install scrapy
```

## Method 1: Simple Python Script (Recommended)

### Basic Usage

```bash
python3 shopify_simple_scraper.py "gymshark.com" --name "Gymshark" --output gymshark_products.json
```

### Multiple Stores

```bash
python3 shopify_simple_scraper.py "gymshark.com,vuoriclothing.com,allbirds.com" --output competitors.json
```

### Advanced Options

```bash
python3 shopify_simple_scraper.py "tentree.com" \
  --name "tentree" \
  --output tentree_products.json \
  --delay 5 \
  --max 100
```

#### Parameters

- `stores`: Comma-separated list of store domains (required)
  - Examples: `"gymshark.com"`, `"www.vuoriclothing.com"`, `"tentree.com"`
- `--name` / `-n`: Competitor name (optional, uses vendor name if not specified)
- `--output` / `-o`: Output JSON file (default: `shopify_products.json`)
- `--delay` / `-d`: Delay between requests in seconds (default: 3)
  - Recommended: 3-5 seconds for politeness
  - Increase if getting rate limited
- `--max` / `-m`: Maximum products to scrape per store (optional)
  - Useful for testing: `--max 50`

### Examples

**Test scraping 20 products from a store:**
```bash
python3 shopify_simple_scraper.py "tentree.com" --max 20 --output test.json
```

**Scrape multiple competitors with a 5-second delay:**
```bash
python3 shopify_simple_scraper.py "gymshark.com,vuoriclothing.com" \
  --output competitors_$(date +%Y%m%d).json \
  --delay 5
```

**Full scrape of a single competitor:**
```bash
python3 shopify_simple_scraper.py "www.tentree.com" \
  --name "tentree Sustainable Apparel" \
  --output ../data/tentree_products.json \
  --delay 3
```

## Method 2: Scrapy Spider (Advanced)

### Basic Usage

```bash
cd scraper
scrapy crawl shopify_competitor -a stores="gymshark.com" -a competitor_name="Gymshark" -o ../data/gymshark.json
```

### Multiple Stores

```bash
scrapy crawl shopify_competitor \
  -a stores="gymshark.com,vuoriclothing.com,allbirds.com" \
  -o ../data/competitors.json
```

### Limit Items (for testing)

```bash
scrapy crawl shopify_competitor \
  -a stores="tentree.com" \
  -a competitor_name="tentree" \
  -s CLOSESPIDER_ITEMCOUNT=50 \
  -o test_tentree.json
```

## How It Works

### Shopify Products JSON API

Shopify exposes a public API endpoint for product data:

```
https://STORE_DOMAIN/products.json?limit=250
```

This endpoint returns structured JSON with all product information including:
- Product ID, title, description
- Variants (colors, sizes, prices)
- Images
- Tags and categories
- Vendor information

### Pagination

Shopify uses **cursor-based pagination** via the `Link` header:

```
Link: <https://store.com/products.json?limit=250&page_info=ABC123>; rel="next"
```

Both scrapers automatically follow pagination links to fetch all products.

### Rate Limiting

**Important:** Be respectful of server resources.

- Default delay: 3-5 seconds between requests
- Maximum concurrency: 1 request at a time per domain
- Increase delays if you receive 429 (Too Many Requests) errors

## Troubleshooting

### 403 Forbidden Errors

**Problem:** Store is blocking automated requests

**Solutions:**
1. Try the simple Python script instead of Scrapy (better success rate)
2. Increase the delay: `--delay 10`
3. Add `www.` prefix: `"www.store.com"` instead of `"store.com"`
4. Some stores have aggressive bot protection - may not be scrapable

### 404 Not Found

**Problem:** Store doesn't expose `/products.json` endpoint

**Solution:** Not all Shopify stores expose this endpoint. Some disable it intentionally. Try:
- Adding or removing `www.` prefix
- If still fails, the store may have disabled the public API

### Brotli Encoding Errors

**Problem:** `HttpCompressionMiddleware cannot decode...from unsupported encoding(s) 'br'`

**Solution:**
```bash
pip install brotli
# or
pip install brotlicffi
```

### Empty Results

**Problem:** Scraper runs but returns 0 products

**Checklist:**
1. Test the endpoint manually:
   ```bash
   curl "https://www.STORE.com/products.json?limit=5" | python3 -m json.tool
   ```
2. Check if store is actually on Shopify (look for `/products.json` working)
3. Try with and without `www.` prefix
4. Check for 403/404 errors in output

### JSON Decode Errors

**Problem:** `Expecting value: line 1 column 1 (char 0)`

**Causes:**
- Getting HTML instead of JSON (403 block page)
- Brotli compression not handled (install `brotli`)
- Endpoint doesn't exist (404)

**Solution:** Check the response preview in error message to see what you're getting.

## Output Format

Both scrapers produce JSON files with the following structure:

```json
[
  {
    "product_id": "123456789",
    "name": "Men's Performance Tee",
    "url": "https://store.com/products/mens-performance-tee",
    "category": "Tops",
    "subcategory": null,
    "gender": "Men",
    "price": 48.0,
    "original_price": 68.0,
    "sale_price": 48.0,
    "currency": "USD",
    "description": "High-performance athletic tee...",
    "colors": ["Black", "Navy", "Charcoal"],
    "sizes": ["S", "M", "L", "XL"],
    "fabrics": [],
    "images": ["https://cdn.shopify.com/..."],
    "is_best_seller": false,
    "best_seller_rank": null,
    "is_homepage_product": false,
    "competitor_name": "Gymshark",
    "store_url": "https://gymshark.com",
    "tags": ["mens", "tops", "performance"],
    "vendor": "Gymshark",
    "scraped_at": "2025-11-12T22:30:00Z"
  }
]
```

## Uploading to Database

After scraping, upload the data to Supabase:

```bash
python database/upload_data.py data/competitors.json
```

## Finding Shopify Stores

To check if a store uses Shopify:

1. Visit the store website
2. Try accessing: `https://STORE_DOMAIN/products.json?limit=1`
3. If you get JSON response with "products" array → it's Shopify!

## Known Working Stores

Based on testing, these approaches work with:

- ✅ **tentree.com** (with `www.` prefix)
- ✅ **gymshark.com** (YMMV - may have bot protection)
- ⚠️ **vuoriclothing.com** (may be blocked)
- ⚠️ **allbirds.com** (strong bot protection)

## Ethical Scraping Guidelines

1. **Respect robots.txt** - The API endpoint is public but still be respectful
2. **Rate limiting** - Use 3-5 second delays minimum
3. **Don't overwhelm servers** - Scrape during off-peak hours if doing large batches
4. **Cache results** - Don't re-scrape unnecessarily
5. **Identify yourself** - The scrapers use proper User-Agent headers
6. **Legal compliance** - Ensure your use case complies with terms of service

## Best Practices

### For Testing

```bash
# Always test with --max first
python3 shopify_simple_scraper.py "STORE.com" --max 20 --output test.json
```

### For Production

```bash
# Use conservative delays and save to data folder
python3 shopify_simple_scraper.py "STORE.com" \
  --name "Competitor Name" \
  --output ../data/competitor_$(date +%Y%m%d).json \
  --delay 5
```

### Automation

Create a bash script for regular competitive analysis:

```bash
#!/bin/bash
# scrape_competitors.sh

DATE=$(date +%Y%m%d)
STORES="tentree.com,vuoriclothing.com"

python3 shopify_simple_scraper.py "$STORES" \
  --output "../data/competitors_${DATE}.json" \
  --delay 5

# Upload to database
python3 ../database/upload_data.py "../data/competitors_${DATE}.json"
```

## Advanced: Customization

### Modify Data Extraction

Edit `parse_product()` function in either scraper to:
- Extract additional fields
- Change gender detection logic
- Add custom categorization

### Add New Fields

Update [items.py](rhone_scraper/items.py) to add new fields to the data model.

### Change Rate Limiting

**Simple scraper:**
```python
scraper = ShopifySimpleScraper(delay=10.0)  # 10 second delay
```

**Scrapy spider:**
```python
custom_settings = {
    'DOWNLOAD_DELAY': 15,  # 15 second delay
}
```

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Test the endpoint manually with `curl`
3. Verify `brotli` is installed
4. Try the simple Python script if Scrapy fails
5. Check if store has disabled the public API

## Future Enhancements

Potential improvements:
- Automatic detection of Shopify stores
- Retry logic for failed requests
- Proxy support for large-scale scraping
- Collection-specific scraping (e.g., `/collections/mens/products.json`)
- CSV output option
- Direct database upload integration
