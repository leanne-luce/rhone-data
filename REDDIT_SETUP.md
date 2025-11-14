# Reddit Brand Sentiment Analysis Setup

This guide explains how to use the Reddit sentiment analysis feature for tracking brand mentions and sentiment on Reddit.

## Features

- **Automated Brand Monitoring**: Scans Reddit for brand mentions across relevant subreddits
- **Sentiment Analysis**: Classifies mentions as Positive, Neutral, or Negative
- **Subreddit Insights**: Identifies where your brand is being discussed most
- **Top Mentions**: Highlights the most upvoted positive and negative posts
- **Time-Series Tracking**: Monitor sentiment trends over time
- **Dashboard Integration**: Results display directly in the Rhone Analysis page

## How It Works

This implementation uses **public Reddit data** - no API credentials required!

- Reddit provides JSON versions of all public pages
- We access these via `https://www.reddit.com/r/subreddit/search.json?q=brand`
- No authentication needed - same data you'd see browsing Reddit logged out
- Respects rate limits with 2-second delays between requests

## Prerequisites

**Python packages** (already included in requirements.txt):
```bash
pip install requests pandas
```

That's it! No API keys or credentials needed.

## Usage

### Generate a Report

Simply run the analysis script:

```bash
python reddit_analysis.py
```

This will:
1. Search for "Rhone" mentions across 10 relevant subreddits
2. Analyze sentiment for each mention (past month by default)
3. Generate a comprehensive report
4. Save results to `data/reddit_report.json`

**Output Example**:
```
============================================================
Reddit Sentiment Analysis: Rhone
============================================================

🔍 Searching for 'Rhone' mentions...
📅 Time period: month
📊 Subreddits: 10

  Searching r/malefashionadvice... ✓ Found 12 mentions
  Searching r/frugalmalefashion... ✓ Found 5 mentions
  Searching r/running... ✓ Found 8 mentions
  ...

✓ Total mentions found: 45
🔬 Analyzing sentiment...
✓ Analysis complete!

============================================================
SUMMARY
============================================================
Brand: Rhone
Time Period: month
Total Mentions: 45

Sentiment Distribution:
  Positive: 28 (62.2%)
  Neutral: 12 (26.7%)
  Negative: 5 (11.1%)

Top Subreddits:
  r/malefashionadvice: 18 mentions
  r/running: 12 mentions
  r/frugalmalefashion: 8 mentions

💾 Report saved to: data/reddit_report.json
```

### View in Dashboard

1. After generating a report, open the Streamlit dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```

2. Navigate to the **Rhone Analysis** page

3. Scroll to the bottom to see the **Reddit Brand Sentiment** section

The dashboard displays:
- **Key Metrics**: Total mentions, sentiment percentages, top subreddit
- **Sentiment Distribution**: Pie chart showing positive/neutral/negative breakdown
- **Top Subreddits**: Bar chart of where mentions occur
- **Top Mentions**: Links to the most upvoted positive and negative posts

### Customizing the Analysis

#### Analyze a Different Brand

```bash
python reddit_analysis.py "Vuori"
python reddit_analysis.py "Lululemon"
```

#### Change Time Period

Edit `reddit_analysis.py` line 339:

```python
# Options: "hour", "day", "week", "month", "year", "all"
report = analyzer.generate_report(time_filter="year", limit_per_subreddit=25)
```

#### Add More Subreddits

Edit `reddit_analysis.py` lines 116-127 to add more subreddits:

```python
subreddits = [
    "malefashionadvice",
    "frugalmalefashion",
    "femalefashionadvice",
    "lululemon",
    "running",
    "fitness",
    "crossfit",
    "yoga",
    "Outlier",
    "goodyearwelt",
    # Add your own:
    "advancedrunning",
    "ultrarunning",
    "veganfitness"
]
```

### Automate Regular Updates

To keep sentiment data fresh, set up a scheduled task:

**Linux/Mac (crontab)**:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/rhone-data && python reddit_analysis.py
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create a new task
3. Set trigger: Daily at 2:00 AM
4. Set action: Run `python reddit_analysis.py` in your project directory

## Monitored Subreddits (Default)

The script searches these subreddits by default:

- **r/malefashionadvice** - Men's fashion discussions
- **r/frugalmalefashion** - Budget-conscious men's fashion
- **r/femalefashionadvice** - Women's fashion discussions
- **r/lululemon** - Lululemon brand discussions (often mentions competitors)
- **r/running** - Running community
- **r/fitness** - General fitness community
- **r/crossfit** - CrossFit community
- **r/yoga** - Yoga practitioners
- **r/Outlier** - Technical apparel enthusiasts
- **r/goodyearwelt** - Quality footwear and apparel

## Sentiment Analysis

The system uses keyword-based sentiment analysis:

**Positive Keywords**: love, great, amazing, excellent, comfortable, quality, recommend, etc.

**Negative Keywords**: hate, terrible, awful, disappointed, uncomfortable, cheap, waste, etc.

**Neutral Keywords**: okay, fine, decent, average, normal, etc.

### How Sentiment is Determined

1. Extract all text (title + post body)
2. Count positive, negative, and neutral keywords
3. Classify based on which category has more matches
4. Calculate confidence score based on keyword frequency

**Example**:
- "I love my Rhone shorts, they're super comfortable and great quality!" → **Positive**
- "Rhone pants are okay but overpriced" → **Neutral**
- "Disappointed with Rhone, poor quality and fell apart" → **Negative**

## Rate Limiting

To respect Reddit's servers:
- **2-second delay** between each subreddit request
- **Max 100 results** per subreddit per search
- **User-Agent header** identifies the scraper

This is well within Reddit's acceptable use and won't trigger rate limiting.

## Troubleshooting

### No Mentions Found

If you're getting 0 mentions:
- **Expand time period**: Try "year" instead of "month"
- **Check brand spelling**: Make sure brand name is spelled correctly
- **Add more subreddits**: Include community-specific or niche subreddits
- **Try brand variations**: "rhone apparel", "rhone.com", etc.

### HTTP 429 (Rate Limit) Errors

If you get rate limited:
- The script already includes 2-second delays
- Wait 5-10 minutes before trying again
- Reduce `limit_per_subreddit` parameter
- Reduce number of subreddits

### Connection Errors

If requests fail:
- Check your internet connection
- Reddit may be temporarily down
- Try again in a few minutes
- Check if Reddit is accessible in your browser

### Empty Sentiment Analysis

If all posts show "Neutral":
- The keyword list may need expansion for your brand
- Edit positive/negative keyword lists in `reddit_analysis.py` (lines 172-185)
- Consider brand-specific terminology (e.g., product names, features)

## Data Privacy & Compliance

**What data is collected:**
- Only public Reddit posts and comments
- Post titles, text content, scores, and URLs
- Public usernames (as displayed on Reddit)

**What is NOT collected:**
- Private messages
- Restricted subreddit content
- User email addresses or personal information
- Any data requiring authentication

**Compliance:**
- Uses publicly accessible data only
- Respects Reddit's robots.txt
- Includes appropriate User-Agent header
- Follows ethical web scraping practices

## Advanced Features (Future Enhancements)

The current implementation provides basic sentiment analysis. Future enhancements could include:

1. **Advanced NLP**: Use transformer models (BERT, RoBERTa) for more accurate sentiment
2. **Aspect-Based Sentiment**: Analyze sentiment by product feature (comfort, price, quality)
3. **Competitor Comparison**: Track and compare sentiment across multiple brands
4. **Real-Time Alerts**: Get notified when sentiment drops or negative mentions spike
5. **Historical Trending**: Track sentiment changes over weeks/months
6. **Influencer Detection**: Identify high-karma users discussing your brand
7. **Comment Analysis**: Analyze comment threads for deeper insights

## Analyzing Other Brands

To analyze competitors:

```bash
# Vuori
python reddit_analysis.py "Vuori"

# Lululemon
python reddit_analysis.py "Lululemon"

# Save to different files
python reddit_analysis.py "Vuori" && mv data/reddit_report.json data/vuori_reddit_report.json
```

## Support

For issues or questions:
1. Check the error message carefully
2. Verify internet connection and Reddit accessibility
3. Review this documentation
4. Check that all dependencies are installed: `pip install -r requirements.txt`

## License

This sentiment analysis tool is part of the Rhone product data analysis project.
