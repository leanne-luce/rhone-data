# Data Collection Reference

## Enhanced Browser Script - What Gets Collected

The enhanced `browser_scraper.js` extracts the following data from Rhone.com collection pages:

### ✅ Product Information
- **Product ID** - Unique identifier from URL
- **Product Name** - Full product title
- **Product URL** - Direct link to product page
- **Category** - Product category (Tops, Bottoms, Shorts, etc.)
- **Gender** - Men's or Women's
- **SKU** - Stock keeping unit

### 💰 Pricing Data
- **Regular Price** - Standard retail price
- **Sale Price** - Discounted price (if on sale)
- **On Sale** - Boolean flag indicating if product is discounted
- **Currency** - USD

### 🎨 Color Options
- **Colors Array** - All available color variants
- Extracted from:
  - Color swatches with data attributes
  - Color dropdowns/selectors  
  - Product name (fallback)

### 📸 Images
- **Product Images** - Primary product image URL
- Clean URLs without query parameters

### 🏷️ Special Indicators
- **Best Seller** - Flag if product has best seller badge
- **Homepage Featured** - Flag if product appears on homepage

### 📊 Metadata
- **Scraped At** - Timestamp of data collection
- **Is Homepage Product** - Boolean for homepage detection

## Data Format Example

```json
{
  "product_id": "commuter-pant-slim",
  "name": "Commuter Pant Slim - Navy",
  "url": "https://www.rhone.com/products/commuter-pant-slim",
  "category": "Bottoms",
  "gender": "Men",
  "price": 128.00,
  "sale_price": 89.60,
  "on_sale": true,
  "currency": "USD",
  "colors": ["Navy", "Black", "Charcoal"],
  "images": ["https://cdn.shopify.com/s/files/1/product-image.jpg"],
  "is_best_seller": false,
  "is_homepage_product": false,
  "sku": "commuter-pant-slim",
  "scraped_at": "2025-11-11T23:00:00.000Z"
}
```

## Collection Pages to Scrape

### Men's Collections
- https://www.rhone.com/collections/mens-tops
- https://www.rhone.com/collections/mens-bottoms
- https://www.rhone.com/collections/mens-shorts
- https://www.rhone.com/collections/mens-outerwear

### Women's Collections
- https://www.rhone.com/collections/womens-tops
- https://www.rhone.com/collections/womens-bottoms
- https://www.rhone.com/collections/womens-outerwear

### Homepage
- https://www.rhone.com/ (for featured products)

## Dashboard Features Using This Data

### Sales & Pricing Analysis (NEW!)
- Products currently on sale
- Discount percentage distribution
- Average discount rates
- Sale products by category
- Biggest discounts

### Color Analysis
- Most popular colors overall
- Colors per category
- Color distribution charts

### Category Analysis  
- Products per category
- Category breakdown by gender

### Best Sellers
- Top products by gender
- Top products by category

### Homepage Products
- Featured products
- Homepage distribution

## Notes on Data Quality

**What works well from collection pages:**
✅ Product names
✅ Prices (regular and sale)
✅ Color options (from swatches)
✅ Images
✅ Sale status
✅ Category/gender info

**What's limited from collection pages:**
⚠️ **Fabrics** - Not usually shown on collection pages
⚠️ **Sizes** - May not be visible without clicking
⚠️ **Detailed descriptions** - Only available on product pages
⚠️ **Best seller rank** - Order-based, not absolute ranking

## Getting Fabric Data

To get fabric information, you have two options:

1. **Use the enrichment script** (may be blocked by Cloudflare):
```bash
python enrich_product_data.py data/rhone_products_combined.json
```

2. **Visit individual product pages** manually for key products

3. **Accept limited data** - Focus on pricing, colors, and categories which are reliably captured

## Data Upload

Once collected:

```bash
# Combine multiple JSON files
python combine_manual_scrapes.py

# Upload to Supabase
python database/upload_data.py

# View in dashboard
python run.py dashboard
```

## Dashboard Visualization

Your collected data powers:
- 8 analysis pages
- Interactive charts
- Filterable tables
- CSV export
- Real-time metrics

All visible at: `http://localhost:8501`
