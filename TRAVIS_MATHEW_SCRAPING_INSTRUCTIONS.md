# Travis Mathew Scraping Instructions

## Quick Start

1. Open a Travis Mathew collection page (e.g., https://travismathew.com/collections/womens-bottoms)
2. Open browser console (F12 or Cmd+Option+I on Mac, F12 on Windows)
3. Copy and paste the entire contents of `browser_scraper_travismathew.js`
4. Press Enter
5. Wait for the script to auto-scroll and extract products
6. JSON file will download automatically

## Troubleshooting

### If you get "No products found"

The script now includes detailed debugging. Check the console output for:

1. **Number of product links found** - If this is 0, the page hasn't loaded yet
2. **Parent hierarchy analysis** - Shows the HTML structure of the first product

### Manual Debugging Steps

If the automatic scraper doesn't work, run these commands in the console to investigate:

```javascript
// 1. Check if product links exist
document.querySelectorAll('a[href*="/products/"]').length

// 2. See the first product link
document.querySelectorAll('a[href*="/products/"]')[0]

// 3. Check the parent structure
document.querySelectorAll('a[href*="/products/"]')[0].parentElement

// 4. Go up several levels to find the product card container
document.querySelectorAll('a[href*="/products/"]')[0].parentElement.parentElement.parentElement
```

### Customizing the Scraper

If the scraper still doesn't work after the above debugging, you may need to customize it:

1. **Find the product container element**
   - Right-click on a product on the page
   - Select "Inspect Element"
   - Look for the container div/li/article that wraps the entire product card
   - Note the class names or tag name

2. **Update the scraper**
   - Open `browser_scraper_travismathew.js`
   - Find the section that says "Try multiple selector strategies"
   - Add a new selector strategy at the top with your discovered class name

Example:
```javascript
// Add this BEFORE the existing selectors
if (productCards.length === 0) {
    productCards = document.querySelectorAll('.your-discovered-class-name');
    console.log(`Try X (custom selector): ${productCards.length} cards`);
}
```

## Expected Output

The scraper will create a JSON file with the following data for each product:

- `brand`: "Travis Mathew"
- `name`: Product name
- `product_id`: Unique identifier from URL
- `url`: Full product URL
- `price`: Regular price (in USD)
- `sale_price`: Sale price if on sale
- `on_sale`: Boolean indicating if product is on sale
- `category`: Auto-detected from URL (e.g., "Bottoms", "Tops")
- `gender`: Auto-detected from URL (e.g., "Women", "Men")
- `colors`: Array of available color options
- `images`: Array of product image URLs
- `badges`: Array of product badges (e.g., "new", "best-seller")
- `review_rating`: Product rating (if available)
- `review_count`: Number of reviews (if available)
- `scraped_at`: Timestamp of when data was collected

## Collection Pages to Scrape

### Women's Collections
- Bottoms: https://travismathew.com/collections/womens-bottoms
- Tops: https://travismathew.com/collections/womens-tops
- Outerwear: https://travismathew.com/collections/womens-outerwear
- Dresses: https://travismathew.com/collections/womens-dresses
- Skirts: https://travismathew.com/collections/womens-skirts

### Men's Collections
- Bottoms: https://travismathew.com/collections/mens-bottoms
- Tops: https://travismathew.com/collections/mens-tops
- Shorts: https://travismathew.com/collections/mens-shorts
- Polos: https://travismathew.com/collections/mens-polos
- Outerwear: https://travismathew.com/collections/mens-outerwear

## After Scraping

1. Save all downloaded JSON files to `data/travismathew-data/` directory
2. Run: `python combine_manual_scrapes.py data/travismathew-data`
3. Upload to database: `python database/upload_data.py`

## Common Issues

### Issue: Page is blank or products aren't loading
**Solution**: Wait a few more seconds for the page to load, then run the script

### Issue: Only getting a few products
**Solution**: The script auto-scrolls, but if the collection is very large, you may need to manually scroll to the very bottom first, wait a few seconds, then run the script

### Issue: Colors aren't being extracted
**Solution**: This is usually okay - we can get color info from the product detail pages later if needed. The scraper tries multiple methods to extract colors from collection pages.

### Issue: Getting duplicate products
**Solution**: The script uses a Set to deduplicate product containers. If you're seeing duplicates in the final JSON, it means the product appears multiple times on the page (this is normal for some sites)

## Tips for Best Results

1. **Use a stable internet connection** - Slow connections may cause lazy-loading issues
2. **Disable browser extensions** - Ad blockers or privacy extensions may interfere with scraping
3. **Use Chrome or Firefox** - Best compatibility with the script
4. **Full screen the browser** - Sometimes helps with lazy-loading detection
5. **Wait for complete page load** - Look for the loading spinner to disappear before running the script
