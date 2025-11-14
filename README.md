# 👕 Rhone Product Analytics Dashboard

A comprehensive data analytics dashboard for analyzing Rhone.com product offerings using web scraping, database storage, and interactive visualizations.

## Overview

This project provides a complete pipeline for:
- **Scraping** product data from Rhone.com using Scrapy
- **Storing** data in Supabase (PostgreSQL database)
- **Analyzing** and visualizing data through an interactive Streamlit dashboard

## Features

### Analytics Capabilities

**Product Overview**
- Total product count
- Products per category
- Category breakdowns by gender

**Color & Fabric Analysis**
- Most commonly offered colors
- Colors per category
- Fabric composition analysis
- Unique fabrics count
- Fabrics per category

**Best Sellers**
- Top 20 best sellers by gender
- Top 5 best sellers per category
- Best seller rankings

**Homepage Analysis**
- Products featured on homepage
- Homepage product distribution by category

**Reddit Brand Sentiment** ✨ NEW
- Monitor brand mentions across Reddit
- Sentiment analysis (Positive, Neutral, Negative)
- Track discussions in relevant subreddits (fashion, fitness, activewear)
- Identify top positive and negative mentions
- View sentiment trends over time
- See [REDDIT_SETUP.md](REDDIT_SETUP.md) for configuration details

## Project Structure

```
rhone-data/
├── scraper/                    # Scrapy web scraper
│   ├── rhone_scraper/
│   │   ├── spiders/
│   │   │   └── rhone_spider.py # Main spider for scraping
│   │   ├── items.py            # Data models
│   │   ├── pipelines.py        # Data processing
│   │   └── settings.py         # Scraper configuration
│   └── scrapy.cfg
├── database/                   # Database utilities
│   ├── schema.sql              # Supabase schema
│   ├── supabase_client.py      # Database client
│   └── upload_data.py          # Data upload script
├── data/                       # Scraped data storage
├── streamlit_app.py            # Main dashboard application
└── requirements.txt            # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy your project URL and anon key
4. Create a `.env` file:

```bash
cp .env.example .env
```

5. Edit `.env` and add your credentials:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional: for Data Chat feature
```

6. Run the database schema in your Supabase SQL Editor:

```bash
# Copy the contents of database/schema.sql and run it in Supabase SQL Editor
```

### 3. Collect Product Data

**⚠️ Important:** Rhone.com uses Cloudflare Turnstile protection that blocks automated scrapers. You have two options:

#### Option A: Manual Collection (Recommended - 15 minutes)

Use your browser's developer tools to extract product data:

```bash
# See detailed instructions
cat MANUAL_SCRAPING.md
```

**Quick steps:**
1. Open https://www.rhone.com/collections/mens-tops in your browser
2. Press `F12` to open Developer Tools
3. Go to Console tab
4. Copy/paste the extraction script from [MANUAL_SCRAPING.md](MANUAL_SCRAPING.md)
5. Press Enter - file downloads automatically
6. Repeat for other collection pages
7. Combine files: `python combine_manual_scrapes.py`

#### Option B: Automated Scraper (May not work due to Cloudflare)

```bash
cd scraper
scrapy crawl rhone
```

**Note:** The automated scraper is set up with Playwright for JavaScript rendering, but Rhone.com's Cloudflare protection typically blocks it. Use Option A (manual collection) for reliable results.

### 4. Upload Data to Supabase

```bash
# Upload the most recent scraped file
python database/upload_data.py

# Or specify a specific file
python database/upload_data.py data/rhone_products_20241111_120000.json
```

### 5. Run the Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Features

### Navigation Pages

1. **Overview** - High-level metrics and category distribution
2. **Category Analysis** - Detailed product breakdown by category and gender
3. **Color Analysis** - Color trends and distribution across categories
4. **Sales & Pricing** - Sales analysis, pricing trends, and promotional insights
5. **Line Plan** - Strategic recommendations and product drop planning
6. **Drop Schedule** - Detailed 12-month product drop calendar with gender-specific assortment breakdowns
7. **Data Chat** - AI-powered chat to ask questions about your product data (requires Anthropic API key)
8. **Raw Data** - Filterable table view with CSV export

### Key Insights

The dashboard answers questions like:
- How many products does Rhone offer?
- What are the most popular colors?
- Which categories have the most items on sale?
- What are the pricing trends by gender and category?
- What strategic recommendations can optimize the product line?

### Data Chat Feature

The **Data Chat** tab provides an AI-powered assistant that can answer custom questions about your product data. It uses Claude AI to analyze your data and provide insights.

**Example questions you can ask:**
- "What's the average price of women's tops?"
- "Which categories have the most products on sale?"
- "What are the most common colors in men's outerwear?"
- "Show me all products under $50"
- "Which gender has more variety in color options?"

**Setup:**
1. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
2. Add it to your `.env` file: `ANTHROPIC_API_KEY=your_key_here`
3. The chat will only reference your actual product data - no hallucinations!

## Data Model

Each product includes:
- Basic info: name, URL, category, subcategory, gender
- Pricing: price, sale price, currency
- Details: description, colors, sizes, fabrics
- Rankings: best seller status and rank
- Images: product image URLs
- Metadata: scrape timestamp, homepage status

## Customization

### Modify Scraper

Edit [scraper/rhone_scraper/spiders/rhone_spider.py](scraper/rhone_scraper/spiders/rhone_spider.py) to:
- Add more collection URLs
- Adjust extraction logic
- Add new data fields

### Extend Dashboard

Edit [streamlit_app.py](streamlit_app.py) to:
- Add new visualizations
- Create custom analytics
- Modify styling and layout

### Database Queries

Use [database/supabase_client.py](database/supabase_client.py) to:
- Add custom query methods
- Create new analytics views
- Export data in different formats

## Technologies Used

- **Scrapy** - Web scraping framework
- **Supabase** - PostgreSQL database (hosted)
- **Streamlit** - Interactive dashboard framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **Python 3.8+** - Programming language

## Ethical Scraping

This scraper:
- Respects robots.txt
- Implements rate limiting (2 second delay)
- Caches responses to minimize requests
- Identifies itself with a proper user agent

## Troubleshooting

### Scraper Issues

If the scraper fails:
1. Check if Rhone.com structure has changed
2. Verify you have internet connectivity
3. Review error messages in the console
4. Adjust selectors in `rhone_spider.py` if needed

### Database Issues

If upload fails:
1. Verify `.env` file has correct credentials
2. Check Supabase project is active
3. Ensure schema has been created
4. Review error messages

### Dashboard Issues

If dashboard shows no data:
1. Confirm data has been uploaded to Supabase
2. Check `.env` credentials
3. Click "Refresh Data" in sidebar
4. Review browser console for errors

## Future Enhancements

Potential additions:
- Price tracking over time
- Inventory monitoring
- Email alerts for new products
- Competitor comparison
- Product recommendation engine
- Automated daily scraping

## License

MIT License - see [LICENSE](LICENSE) file for details
