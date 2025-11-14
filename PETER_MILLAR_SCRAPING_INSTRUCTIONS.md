# Peter Millar Web Scraper Instructions

This guide will help you scrape product data from Peter Millar's website.

## Quick Start

1. **Open the Peter Millar collection page** you want to scrape in your browser
   - Example: https://www.petermillar.com/c/women/tops

2. **Open the browser console**
   - Chrome/Edge: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Firefox: Press `F12` or `Cmd+Option+K` (Mac) / `Ctrl+Shift+K` (Windows)
   - Safari: Enable Developer menu in Preferences, then press `Cmd+Option+I`

3. **Copy and paste the scraper script**
   - Open the file: `browser_scraper_petermillar.js`
   - Copy the entire contents
   - Paste into the browser console
   - Press Enter

4. **Wait for the script to complete**
   - The script will auto-scroll to load all products
   - You'll see progress messages in the console
   - A JSON file will automatically download when complete

5. **Save the downloaded file**
   - Move it to the `data/petermillar-data/` directory in this project

## Collection Pages to Scrape

### Women's Collections
- Tops: https://www.petermillar.com/c/women/tops
- Bottoms: https://www.petermillar.com/c/women/bottoms
- Dresses: https://www.petermillar.com/c/women/dresses
- Skirts: https://www.petermillar.com/c/women/skirts
- Outerwear: https://www.petermillar.com/c/women/outerwear
- Sweaters: https://www.petermillar.com/c/women/sweaters

### Men's Collections
- Tops: https://www.petermillar.com/c/men/tops
- Bottoms: https://www.petermillar.com/c/men/bottoms
- Shorts: https://www.petermillar.com/c/men/shorts
- Outerwear: https://www.petermillar.com/c/men/outerwear
- Sweaters: https://www.petermillar.com/c/men/sweaters

## After Scraping All Collections

1. **Combine all scraped files into one dataset**
   ```bash
   python combine_manual_scrapes.py
   ```
   This will create a combined JSON file with all products from all brands (Rhone, Vuori, Lululemon, Peter Millar).

2. **Upload to Supabase database**
   ```bash
   python database/upload_data.py data/rhone_products_combined_YYYYMMDD_HHMMSS.json
   ```

3. **Launch the dashboard to view the data**
   ```bash
   python run.py dashboard
   ```

## Troubleshooting

### "No products found"
- Make sure you're on a collection page (URL should be `/c/...`)
- Wait for the page to fully load before running the script
- Try scrolling down manually first to trigger lazy loading
- Check if Peter Millar has updated their website structure

### Incapsula/Cloudflare blocking
Peter Millar uses Incapsula protection. If you get blocked:
- Clear your browser cookies and cache
- Try using a different browser
- Wait a few minutes between scraping different pages
- Use your browser's regular (non-incognito) mode

### Missing data in scraped results
- Some fields (like colors, prices) may not be extracted if Peter Millar changes their HTML structure
- The script includes multiple fallback strategies, but you may need to inspect the page HTML and update the selectors

## Data Structure

Each product will have the following fields:
- `brand`: "Peter Millar"
- `name`: Product name
- `price`: Regular price (USD)
- `sale_price`: Sale price if on sale
- `on_sale`: Boolean indicating if product is on sale
- `colors`: Array of available colors
- `sizes`: Array of available sizes (currently empty, can be enhanced)
- `category`: Product category (Tops, Bottoms, etc.)
- `gender`: "Women" or "Men"
- `url`: Product page URL
- `product_id`: Unique product identifier
- `images`: Array of product image URLs
- `badges`: Array of badges (new, best-seller, sale, etc.)
- `scraped_at`: ISO timestamp of when data was scraped

## Notes

- The scraper automatically detects gender and category from the URL path
- It auto-scrolls to load all lazy-loaded products
- Duplicate products (same URL) are automatically merged
- The script is based on the same pattern used for Vuori and Lululemon scrapers
