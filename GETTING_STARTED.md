# Getting Started with Rhone Product Analytics

Welcome! This guide will get you from zero to a working dashboard in about 30 minutes.

## What You'll Build

A complete analytics dashboard that shows:
- Product counts and categories
- Color and fabric analysis  
- Best sellers rankings
- Homepage featured products

## Prerequisites

- Python 3.8+ installed
- A browser (Chrome, Firefox, or Safari)
- A free Supabase account

## Step-by-Step Setup

### 1. Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase (5 minutes)

**A. Create Account & Project**
1. Go to [supabase.com](https://supabase.com) and sign up
2. Click "New Project"
3. Choose a name and password
4. Wait for setup to complete (~2 minutes)

**B. Get Your Credentials**
1. Go to Settings → API
2. Copy your "Project URL"
3. Copy your "anon public" key

**C. Configure Environment**
```bash
cp .env.example .env
# Edit .env and paste your credentials
```

**D. Create Database Tables**
1. In Supabase, go to SQL Editor
2. Copy all content from `database/schema.sql`
3. Paste into SQL Editor
4. Click "Run"

### 3. Collect Product Data (15 minutes)

**⚠️ Important:** Rhone.com blocks automated scrapers, so we'll collect data manually through your browser.

**Follow these steps:**

1. Open your browser to: https://www.rhone.com/collections/mens-tops

2. Press `F12` (or `Cmd+Option+I` on Mac) to open Developer Tools

3. Click the "Console" tab

4. Open `MANUAL_SCRAPING.md` and copy the JavaScript extraction script

5. Paste the script into the console and press Enter

6. A JSON file will download automatically

7. Save it to the `data/` directory

8. Repeat steps 1-7 for these pages:
   - Men's Bottoms: https://www.rhone.com/collections/mens-bottoms
   - Men's Shorts: https://www.rhone.com/collections/mens-shorts
   - Women's Tops: https://www.rhone.com/collections/womens-tops
   - Women's Bottoms: https://www.rhone.com/collections/womens-bottoms
   - Homepage: https://www.rhone.com/

9. Combine all your JSON files:
```bash
python combine_manual_scrapes.py
```

### 4. Upload to Database (1 minute)

```bash
python database/upload_data.py
```

This uploads your collected data to Supabase.

### 5. Launch Dashboard (instant)

```bash
python run.py dashboard
```

Your browser will open to `http://localhost:8501` with the dashboard!

## What to Explore

Once the dashboard loads, check out:

1. **Overview** - See total products and key metrics
2. **Color Analysis** - Most popular colors by category
3. **Fabric Analysis** - Material composition insights
4. **Best Sellers** - Top products by gender and category
5. **Raw Data** - Filter and export product data

## Troubleshooting

**"No data available" error:**
- Make sure you ran step 4 (upload to Supabase)
- Check your .env file has correct Supabase credentials
- Verify data files exist in the `data/` directory

**JavaScript extraction script doesn't work:**
- Make sure you're on a collection page (not a product page)
- Scroll down to load all products first
- Check the browser console for error messages

**Database connection error:**
- Verify .env credentials are correct
- Check your Supabase project is active
- Make sure you ran the schema.sql in Supabase

**Python import errors:**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

## Alternative: Use Sample Data

If you want to see the dashboard immediately without collecting real data:

```bash
python create_sample_data.py
python database/upload_data.py
python run.py dashboard
```

This generates 100 sample products so you can explore the dashboard features.

## Next Steps

Once your dashboard is running:

1. **Customize the analytics** - Edit `streamlit_app.py` to add new visualizations
2. **Schedule updates** - Set up daily scraping with the manual method
3. **Export insights** - Use the CSV export feature in the Raw Data page
4. **Extend the scraper** - Add more product attributes to track

## Need Help?

- Read the full documentation: [README.md](README.md)
- Manual scraping guide: [MANUAL_SCRAPING.md](MANUAL_SCRAPING.md)
- System architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Quick start: [QUICKSTART.md](QUICKSTART.md)

## Files Overview

```
Key files you'll use:
├── GETTING_STARTED.md        ← You are here
├── MANUAL_SCRAPING.md         ← Browser extraction guide
├── .env                       ← Your credentials (create this)
├── data/                      ← Save JSON files here
├── database/schema.sql        ← Run this in Supabase
├── combine_manual_scrapes.py  ← Combine JSON files
└── streamlit_app.py           ← The dashboard
```

Happy analyzing! 🎉
