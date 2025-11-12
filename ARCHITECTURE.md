# System Architecture

## Overview

The Rhone Product Analytics Dashboard consists of three main components that work together to scrape, store, and visualize product data.

```
┌─────────────────────────────────────────────────────────────────┐
│                     RHONE PRODUCT ANALYTICS                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│              │      │              │      │              │
│   SCRAPER    │─────▶│   DATABASE   │─────▶│  DASHBOARD   │
│   (Scrapy)   │      │  (Supabase)  │      │ (Streamlit)  │
│              │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       │                     │                      │
   rhone.com          PostgreSQL DB         Web Interface
```

## Component Details

### 1. Web Scraper (Scrapy)

**Purpose:** Extract product data from Rhone.com

**Technology:** Scrapy (Python web scraping framework)

**Components:**
- `rhone_spider.py` - Main spider that crawls product pages
- `items.py` - Data models defining product structure
- `pipelines.py` - Data processing and JSON export
- `settings.py` - Configuration (rate limiting, user agent, etc.)

**Process:**
1. Start with collection pages and homepage
2. Extract product links
3. Visit each product page
4. Extract product details using CSS selectors
5. Process and validate data
6. Save to JSON file in `data/` directory

**Features:**
- Respects robots.txt
- Rate limiting (2 second delay)
- HTTP caching for development
- Automatic retry on failures
- Tracks homepage featured products

### 2. Database (Supabase)

**Purpose:** Store and manage product data

**Technology:** Supabase (hosted PostgreSQL)

**Schema:**
```sql
products
├── id (primary key)
├── product_id (unique)
├── name
├── url
├── category
├── subcategory
├── gender
├── price
├── sale_price
├── currency
├── description
├── colors (JSONB array)
├── sizes (JSONB array)
├── fabrics (JSONB array)
├── best_seller_rank
├── is_best_seller
├── images (JSONB array)
├── scraped_at
├── is_homepage_product
├── sku
├── availability
├── created_at
└── updated_at
```

**Indexes:**
- Category, gender, best_seller, homepage, scraped_at
- For fast querying on common filters

**Views:**
- `color_analysis` - Pre-aggregated color statistics
- `fabric_analysis` - Pre-aggregated fabric statistics
- `best_sellers` - Ranked best selling products

**Client API:**
- `SupabaseClient` class provides high-level methods
- CRUD operations
- Filtering and querying
- Batch operations

### 3. Dashboard (Streamlit)

**Purpose:** Interactive data visualization and analysis

**Technology:** Streamlit (Python web framework)

**Visualization Libraries:**
- Plotly - Interactive charts
- Pandas - Data manipulation
- Altair - Statistical visualizations

**Pages:**

1. **Overview**
   - Key metrics (total products, categories, best sellers)
   - Category distribution

2. **Category Analysis**
   - Products by category
   - Category breakdown by gender
   - Bar charts and tables

3. **Color Analysis**
   - Top 20 most common colors
   - Colors per category
   - Color distribution visualizations

4. **Fabric Analysis**
   - Unique fabrics count
   - Most common fabrics
   - Fabrics per category

5. **Best Sellers**
   - Top 20 by gender (tabs)
   - Top 5 per category (expandable)
   - Product details tables

6. **Homepage Products**
   - Homepage featured products
   - Distribution by category
   - Product listings

7. **Raw Data**
   - Filterable data table
   - CSV export
   - Full product details

**Features:**
- Real-time data loading from Supabase
- Caching for performance (1 hour TTL)
- Responsive design
- Interactive filters
- Data refresh button

## Data Flow

### Initial Setup
```
1. User sets up Supabase project
   └─▶ Creates database schema

2. User configures .env file
   └─▶ Adds Supabase credentials
```

### Regular Operation
```
1. Run Scraper
   ├─▶ Visits Rhone.com
   ├─▶ Extracts product data
   └─▶ Saves to JSON file

2. Upload Data
   ├─▶ Reads JSON file
   ├─▶ Processes data
   └─▶ Upserts to Supabase

3. View Dashboard
   ├─▶ Loads data from Supabase
   ├─▶ Processes and aggregates
   └─▶ Renders visualizations
```

## File Structure

```
rhone-data/
│
├── scraper/                    # Web scraping component
│   ├── rhone_scraper/
│   │   ├── spiders/
│   │   │   ├── __init__.py
│   │   │   └── rhone_spider.py    # Main spider
│   │   ├── __init__.py
│   │   ├── items.py               # Data models
│   │   ├── pipelines.py           # Data processing
│   │   └── settings.py            # Configuration
│   ├── httpcache/                 # HTTP cache (gitignored)
│   └── scrapy.cfg                 # Scrapy config
│
├── database/                   # Database component
│   ├── __init__.py
│   ├── schema.sql                 # Database schema
│   ├── supabase_client.py         # Database client
│   └── upload_data.py             # Upload script
│
├── data/                       # Scraped data (gitignored)
│   └── rhone_products_*.json
│
├── dashboard/                  # Dashboard utilities
│   └── __init__.py
│
├── .github/
│   └── workflows/
│       └── scrape_daily.yml.example  # CI/CD example
│
├── streamlit_app.py            # Main dashboard app
├── run.py                      # Convenience script
├── analysis_example.py         # Example analysis script
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .env                        # Environment variables (gitignored)
│
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
└── ARCHITECTURE.md             # This file
```

## Technology Stack

### Core Technologies
- **Python 3.8+** - Programming language
- **Scrapy 2.11+** - Web scraping framework
- **Supabase** - Backend as a Service (PostgreSQL)
- **Streamlit 1.28+** - Dashboard framework

### Data Processing
- **Pandas 2.0+** - Data manipulation
- **JSON** - Data serialization

### Visualization
- **Plotly 5.17+** - Interactive charts
- **Altair 5.0+** - Statistical visualizations

### Database
- **PostgreSQL** - Relational database (via Supabase)
- **JSONB** - JSON data type for arrays

### Utilities
- **python-dotenv** - Environment variable management
- **requests** - HTTP library

## Scalability Considerations

### Current Implementation
- Single-threaded scraping
- Synchronous database operations
- In-memory data processing
- Suitable for: 100-10,000 products

### For Larger Scale (10,000+ products)
1. **Scraping:**
   - Enable concurrent requests in Scrapy
   - Use distributed scraping (ScrapyCloud)
   - Implement incremental updates

2. **Database:**
   - Add pagination to queries
   - Use database views for aggregations
   - Consider materialized views for performance

3. **Dashboard:**
   - Implement server-side pagination
   - Add query result limits
   - Use more aggressive caching
   - Consider Redis for caching layer

## Security Considerations

### Implemented
- Environment variables for credentials
- `.env` file in `.gitignore`
- Rate limiting on scraper
- Respects robots.txt

### Best Practices
- Use Supabase Row Level Security (RLS)
- Rotate API keys regularly
- Don't commit credentials
- Use HTTPS for all connections

## Monitoring and Maintenance

### Logs
- Scrapy logs: Console output during scraping
- Streamlit logs: Console output when running
- Supabase logs: Available in Supabase dashboard

### Error Handling
- Scraper: Automatic retries on failures
- Database: Try-catch blocks with error messages
- Dashboard: Error messages displayed to user

### Updates
- Scrapy selectors may need updates if Rhone.com changes
- Dependencies should be updated regularly
- Test after any Rhone.com redesign

## Future Enhancements

### Planned Features
1. **Historical Tracking**
   - Track price changes over time
   - Monitor product availability
   - Detect new products

2. **Alerts**
   - Email notifications for price drops
   - Alerts for new products
   - Inventory alerts

3. **Advanced Analytics**
   - Trend analysis
   - Seasonal patterns
   - Predictive analytics

4. **Automation**
   - Scheduled scraping (cron/GitHub Actions)
   - Automatic reports
   - Data quality checks

5. **Enhancements**
   - Product images in dashboard
   - Customer reviews analysis
   - Comparison with competitors
   - API endpoint for external access

## Support and Maintenance

### Common Issues

**Scraper not working:**
- Check if Rhone.com structure changed
- Update CSS selectors in spider
- Verify robots.txt compliance

**Database connection issues:**
- Verify .env credentials
- Check Supabase project status
- Ensure network connectivity

**Dashboard showing no data:**
- Confirm data has been uploaded
- Check Supabase connection
- Verify data in database

### Contributing

To extend this project:
1. Fork the repository
2. Add new features
3. Test thoroughly
4. Submit pull request

For questions or issues, refer to the main [README.md](README.md).
