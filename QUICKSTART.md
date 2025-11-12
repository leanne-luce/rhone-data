# Quick Start Guide

Get up and running with the Rhone Product Analytics Dashboard in 5 steps.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A Supabase account (free tier works great)

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

Or use the convenience script:

```bash
python run.py install
```

### 2. Configure Supabase (5 minutes)

**A. Create Supabase Project**
1. Go to [supabase.com](https://supabase.com) and sign up
2. Click "New Project"
3. Choose a name and password
4. Wait for project to finish setting up

**B. Get Your Credentials**
1. In your Supabase project, go to Settings → API
2. Copy your Project URL
3. Copy your `anon` `public` key

**C. Configure Environment**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your credentials
# SUPABASE_URL=https://xxxxx.supabase.co
# SUPABASE_KEY=eyJxxx...
```

**D. Create Database Schema**
1. In Supabase, go to SQL Editor
2. Open [database/schema.sql](database/schema.sql)
3. Copy all the SQL code
4. Paste it into Supabase SQL Editor
5. Click "Run"

### 3. Scrape Product Data (5-10 minutes)

```bash
python run.py scrape
```

This will:
- Visit Rhone.com and collect product data
- Save results to `data/rhone_products_YYYYMMDD_HHMMSS.json`
- Be respectful with rate limiting

**What gets scraped:**
- Product names, URLs, categories
- Prices and sale prices
- Colors and sizes available
- Fabric information
- Best seller status
- Product images

### 4. Upload to Database (1 minute)

```bash
python run.py upload
```

This uploads the scraped data to your Supabase database.

### 5. Launch Dashboard (instant)

```bash
python run.py dashboard
```

The dashboard will open in your browser at `http://localhost:8501`

## What You Can Do Now

### Explore the Analytics

**Overview Page**
- See total product count
- View category distribution
- Check homepage featured products

**Color Analysis**
- Top 20 most common colors
- Colors by category
- Color trends

**Fabric Analysis**
- Fabric composition breakdown
- Most used materials
- Fabrics per category

**Best Sellers**
- Top 20 by gender
- Top 5 per category
- Best seller rankings

**Homepage Products**
- Products featured on homepage
- Homepage distribution analysis

**Raw Data**
- Filter by category, gender, best seller status
- Export to CSV
- Full product details

## Updating Data

To refresh with the latest products from Rhone.com:

```bash
# Scrape fresh data
python run.py scrape

# Upload to database (replaces existing data)
python run.py upload

# In the dashboard, click "Refresh Data" in the sidebar
```

## Troubleshooting

### "No data available" in dashboard

**Solution:** Make sure you've completed steps 3 and 4 (scrape and upload)

### Supabase connection error

**Solution:** Check your `.env` file has the correct credentials

### Scraper not finding products

**Solution:** Rhone.com may have changed their HTML structure. You may need to update the CSS selectors in [scraper/rhone_scraper/spiders/rhone_spider.py](scraper/rhone_scraper/spiders/rhone_spider.py)

### Import errors

**Solution:** Reinstall dependencies: `pip install -r requirements.txt`

## Advanced Usage

### Custom Queries

Use the Supabase client directly:

```python
from database.supabase_client import SupabaseClient

client = SupabaseClient()

# Get all black products
black_products = client.get_products_by_color("black")

# Get men's tops
mens_tops = client.get_products_by_category("Tops")
```

### Modify the Scraper

Edit [scraper/rhone_scraper/spiders/rhone_spider.py](scraper/rhone_scraper/spiders/rhone_spider.py):

- Add more collection URLs to `start_urls`
- Adjust CSS selectors if site structure changes
- Add new fields to extract

### Customize the Dashboard

Edit [streamlit_app.py](streamlit_app.py):

- Add new visualizations
- Create custom metrics
- Change color schemes
- Add filtering options

## Next Steps

- Set up automated daily scraping (cron job or GitHub Actions)
- Add price tracking to monitor changes over time
- Create email alerts for new products
- Compare with competitor data
- Build a recommendation engine

## Need Help?

Check the full [README.md](README.md) for detailed documentation.

## Project Structure Quick Reference

```
rhone-data/
├── scraper/               # Web scraping
│   └── rhone_scraper/
│       └── spiders/
│           └── rhone_spider.py  # Main scraper
├── database/              # Database management
│   ├── schema.sql         # Database schema
│   ├── supabase_client.py # Database client
│   └── upload_data.py     # Upload script
├── streamlit_app.py       # Dashboard
├── run.py                 # Convenience script
└── requirements.txt       # Dependencies
```

Happy analyzing!
