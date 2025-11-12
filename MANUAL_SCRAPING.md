# Manual Data Collection Guide for Rhone.com

Since Rhone.com uses Cloudflare Turnstile protection that blocks automated scrapers, you can collect the data manually using your browser's developer tools.

## Method 1: Browser Console Script (Recommended - 15 minutes)

This method uses a JavaScript script you run in your browser to extract product data.

### Step 1: Navigate to a Collection Page

Open your browser and go to one of these pages:
- https://www.rhone.com/collections/mens-tops
- https://www.rhone.com/collections/mens-bottoms
- https://www.rhone.com/collections/womens-tops
- etc.

### Step 2: Open Developer Tools

- **Chrome/Edge:** Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Firefox:** Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- **Safari:** Enable Developer Menu first (Safari → Preferences → Advanced → Show Develop menu), then press `Cmd+Option+I`

### Step 3: Go to Console Tab

Click on the "Console" tab in the developer tools.

### Step 4: Run the Extraction Script

**Option A: Copy from file (Recommended)**

The enhanced script is saved in `browser_scraper.js`. Open it, copy all contents, paste into console, and press Enter.

```bash
cat browser_scraper.js
```

**Option B: Use inline script**

Or copy and paste this entire script directly into the console and press Enter:

```javascript
// Product extraction script for Rhone.com
(function() {
    console.log('Starting product extraction...');

    const products = [];

    // Find all product links on the page
    const productLinks = document.querySelectorAll('a[href*="/products/"]');
    const uniqueLinks = new Set();

    productLinks.forEach(link => {
        const href = link.href;
        if (href && href.includes('/products/')) {
            uniqueLinks.add(href);
        }
    });

    console.log(`Found ${uniqueLinks.size} unique product links`);

    // Extract product IDs from URLs
    uniqueLinks.forEach(url => {
        const match = url.match(/\/products\/([^?#]+)/);
        if (match) {
            products.push({
                url: url,
                product_id: match[1],
                scraped_at: new Date().toISOString(),
                is_homepage_product: window.location.pathname === '/',
            });
        }
    });

    // Try to get more details from product cards
    const productCards = document.querySelectorAll('[class*="product-card"], [class*="ProductCard"], .product-item, [data-product-id]');

    productCards.forEach(card => {
        const link = card.querySelector('a[href*="/products/"]');
        const title = card.querySelector('[class*="title"], [class*="name"], h2, h3, h4');
        const price = card.querySelector('[class*="price"]');
        const image = card.querySelector('img');

        if (link) {
            const url = link.href;
            const productId = url.match(/\/products\/([^?#]+)/)?.[1];

            const existing = products.find(p => p.product_id === productId);
            if (existing) {
                existing.name = title?.textContent?.trim() || null;
                existing.price = price?.textContent?.trim() || null;
                existing.image = image?.src || null;

                // Try to determine category and gender from URL
                const urlLower = window.location.pathname.toLowerCase();
                if (urlLower.includes('mens') || urlLower.includes('/men')) {
                    existing.gender = 'Men';
                } else if (urlLower.includes('womens') || urlLower.includes('/women')) {
                    existing.gender = 'Women';
                }

                if (urlLower.includes('tops')) existing.category = 'Tops';
                else if (urlLower.includes('bottoms')) existing.category = 'Bottoms';
                else if (urlLower.includes('shorts')) existing.category = 'Shorts';
                else if (urlLower.includes('outerwear')) existing.category = 'Outerwear';
            }
        }
    });

    console.log(`Extracted ${products.length} products`);

    // Download as JSON
    const dataStr = JSON.stringify(products, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `rhone_products_${window.location.pathname.replace(/\//g, '_')}_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('Download started!');
    return products;
})();
```

### Step 5: Download the Data

The script will automatically download a JSON file with the product data.

### Step 6: Repeat for Other Categories

Run the script on each collection page:
- Men's Tops
- Men's Bottoms
- Men's Shorts
- Men's Outerwear
- Women's Tops
- Women's Bottoms
- Women's Outerwear
- Homepage (for featured products)

### Step 7: Combine the Files

Use this Python script to combine all your JSON files:

```bash
cd /Users/leanneluce/code/rhone-data
python combine_manual_scrapes.py
```

---

## Method 2: Network Tab Inspection (Advanced - 30 minutes)

This method captures the actual API calls Rhone.com makes to load products.

### Step 1: Open Developer Tools

Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)

### Step 2: Go to Network Tab

Click on the "Network" tab.

### Step 3: Filter for API Calls

In the filter box at the top, type: `products` or `collections`

### Step 4: Browse Collection Pages

Navigate to: https://www.rhone.com/collections/mens-tops

### Step 5: Find Product API Calls

Look for XHR/Fetch requests that return JSON data with product information. Common patterns:
- `/products.json`
- `/collections/*/products.json`
- API endpoints with product data

### Step 6: Copy Response

1. Click on the API request
2. Go to the "Response" tab
3. Right-click the JSON data
4. Select "Copy" or "Copy object"

### Step 7: Save to File

Create a new file: `data/rhone_api_response.json` and paste the data.

### Step 8: Convert Format

Use the conversion script:

```bash
python convert_api_format.py data/rhone_api_response.json
```

---

## Method 3: Browser Extension (Easiest - 5 minutes)

Use a browser extension to extract product data:

### Recommended Extensions:

**For Chrome/Edge:**
- **Web Scraper** - https://chrome.google.com/webstore (search "Web Scraper")
- **Data Scraper** - https://chrome.google.com/webstore (search "Data Scraper")

**For Firefox:**
- **Scraper** - https://addons.mozilla.org (search "Scraper")

### Using Web Scraper Extension:

1. Install the extension
2. Click the extension icon
3. Create New Sitemap
4. Add starting URL: https://www.rhone.com/collections/mens-tops
5. Add selectors:
   - Product links: `a[href*="/products/"]`
   - Product name: `.product-title, h2, h3`
   - Price: `[class*="price"]`
   - Image: `img`
6. Start scraping
7. Export as JSON

---

## Helper Scripts

I've created helper scripts to process your manually collected data.

### Combine Multiple JSON Files

```python
# File: combine_manual_scrapes.py
import json
import glob
from pathlib import Path
from datetime import datetime

def combine_manual_scrapes():
    """Combine multiple manually scraped JSON files"""

    # Find all JSON files in data directory
    json_files = glob.glob("data/rhone_products_*.json")

    if not json_files:
        print("No JSON files found in data/ directory")
        print("Make sure to save your browser-extracted files there.")
        return

    all_products = []
    seen_ids = set()

    for file_path in json_files:
        print(f"Reading {file_path}...")
        with open(file_path, 'r') as f:
            try:
                products = json.load(f)
                if isinstance(products, list):
                    for product in products:
                        product_id = product.get('product_id')
                        if product_id and product_id not in seen_ids:
                            all_products.append(product)
                            seen_ids.add(product_id)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")

    print(f"\nCombined {len(all_products)} unique products from {len(json_files)} files")

    # Save combined file
    output_file = f"data/rhone_products_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_products, f, indent=2)

    print(f"Saved to: {output_file}")
    print("\nNext step: python database/upload_data.py")

if __name__ == "__main__":
    combine_manual_scrapes()
```

### Enrich Product Data

Once you have product URLs, this script visits each one to get detailed info:

```python
# File: enrich_product_data.py
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def enrich_products(input_file):
    """
    WARNING: This script makes HTTP requests and may still be blocked by Cloudflare.
    Use it carefully and add delays between requests.
    """

    with open(input_file, 'r') as f:
        products = json.load(f)

    print(f"Enriching {len(products)} products...")
    print("This will take a while (2-3 seconds per product)")

    for i, product in enumerate(products):
        if 'name' not in product or not product.get('name'):
            print(f"\nFetching details for product {i+1}/{len(products)}: {product['url']}")

            try:
                # Add delay to be respectful
                time.sleep(3)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(product['url'], headers=headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract product name
                    title = soup.find('h1')
                    if title:
                        product['name'] = title.get_text(strip=True)

                    # Extract price
                    price = soup.find(class_=lambda x: x and 'price' in x.lower())
                    if price:
                        product['price'] = price.get_text(strip=True)

                    print(f"  ✓ Got: {product.get('name', 'Unknown')}")
                else:
                    print(f"  ✗ Error: HTTP {response.status_code}")

            except Exception as e:
                print(f"  ✗ Error: {e}")

    # Save enriched data
    output_file = input_file.replace('.json', '_enriched.json')
    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"\nSaved enriched data to: {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python enrich_product_data.py <json_file>")
    else:
        enrich_products(sys.argv[1])
```

---

## Quick Start Summary

**Fastest way to get data (5-10 minutes):**

1. Open https://www.rhone.com/collections/mens-tops
2. Press `F12` to open developer tools
3. Click Console tab
4. Copy and paste the extraction script above
5. Press Enter
6. File downloads automatically
7. Repeat for 5-6 main collection pages
8. Run: `python combine_manual_scrapes.py`
9. Run: `python database/upload_data.py`
10. Run: `python run.py dashboard`

---

## Tips for Success

1. **Work in a private/incognito window** - Fresh session without cookies
2. **Scroll to load all products** - Some sites lazy-load content
3. **Check console for errors** - Fix any JavaScript errors
4. **Save files to data/ directory** - So scripts can find them
5. **Be patient** - Manual collection takes time but works 100%

---

## Troubleshooting

**Script doesn't find products:**
- Scroll down to ensure all products are loaded
- Try a different collection page
- Check if the page uses different HTML structure

**Download doesn't start:**
- Check browser's download settings
- Try manually copying console output and saving to file
- Look for browser popup blocker

**Empty or minimal data:**
- Run the script after the page fully loads
- Try visiting individual product pages for more details

---

## Need Help?

If you get stuck, you can:
1. Check the browser console for error messages
2. Try a simpler page first (fewer products)
3. Use the sample data generator: `python create_sample_data.py`
4. Review the README for alternative approaches
