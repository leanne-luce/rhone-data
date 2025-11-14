# Lululemon Manual Scraping Guide

## Quick Start

1. **Open browser scraper script**: Open [browser_scraper_lululemon.js](browser_scraper_lululemon.js) in your code editor
2. **Copy the entire script**
3. **Navigate to a Lululemon collection page** (examples below)
4. **Open browser console**: Press F12 or Cmd+Option+I
5. **Paste the script** and press Enter
6. **Wait for completion** - The script will download a JSON file
7. **Save the file** to `data/lululemon-data/` directory

## Collection Pages to Scrape

### Men's Collections
- **Tops**: https://shop.lululemon.com/c/men-tops
- **Shirts**: https://shop.lululemon.com/c/men-button-down-shirts
- **Polos**: https://shop.lululemon.com/c/men-polos
- **T-Shirts**: https://shop.lululemon.com/c/men-t-shirts
- **Pants**: https://shop.lululemon.com/c/men-pants
- **Joggers**: https://shop.lululemon.com/c/men-joggers
- **Shorts**: https://shop.lululemon.com/c/men-shorts
- **Jackets & Hoodies**: https://shop.lululemon.com/c/men-jackets-and-hoodies
- **Bags**: https://shop.lululemon.com/c/men-bags

### Women's Collections
- **Tops**: https://shop.lululemon.com/c/women-tops
- **T-Shirts**: https://shop.lululemon.com/c/women-t-shirts
- **Tank Tops**: https://shop.lululemon.com/c/women-tank-tops
- **Long Sleeve**: https://shop.lululemon.com/c/women-long-sleeve-shirts
- **Sports Bras**: https://shop.lululemon.com/c/women-sports-bras
- **Leggings**: https://shop.lululemon.com/c/women-leggings
- **Pants**: https://shop.lululemon.com/c/women-pants
- **Joggers**: https://shop.lululemon.com/c/women-joggers
- **Shorts**: https://shop.lululemon.com/c/women-shorts
- **Dresses**: https://shop.lululemon.com/c/women-dresses-and-jumpsuits
- **Jackets & Hoodies**: https://shop.lululemon.com/c/women-jackets-and-hoodies
- **Bags**: https://shop.lululemon.com/c/women-bags
- **Hats**: https://shop.lululemon.com/c/women-hats

### Sale Section (We Made Too Much)
- **Men's WMTM**: https://shop.lululemon.com/c/men-we-made-too-much
- **Women's WMTM**: https://shop.lululemon.com/c/women-we-made-too-much

## After Scraping

Once you've scraped all the desired collections:

1. **Combine the data**:
   ```bash
   python combine_manual_scrapes.py data/lululemon-data
   ```

2. **Upload to Supabase**:
   ```bash
   python database/upload_data.py data/lululemon_products_combined_TIMESTAMP.json
   ```

3. **View in dashboard**: The Lululemon data will appear in the dashboard alongside Rhone and Vuori

## Tips

- **Scroll to the bottom** of each page before running the script to ensure all lazy-loaded products are visible
- **Wait 2-3 seconds** after scrolling before pasting the script
- Each file will be named with the collection path and timestamp (e.g., `lululemon_products_c_men-button-down-shirts_1234567890.json`)
- The script automatically detects:
  - Gender (Men/Women) from URL
  - Category (Tops, Bottoms, Shorts, etc.) from URL
  - Product colors, prices, sale status, and images

## What Gets Extracted

- Product name
- URL and product ID
- Category and gender
- Price and sale price
- Colors available
- Product images
- Reviews/ratings
- Badges (new, sale, WMTM, etc.)
- Brand: "Lululemon"
