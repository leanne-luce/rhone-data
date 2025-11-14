#!/usr/bin/env python3
"""
Reddit Brand Sentiment Analysis Module

Monitors and analyzes brand mentions across Reddit using public JSON endpoints.
No API credentials required - uses publicly accessible Reddit data.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import json
import re


class RedditAnalyzer:
    """Analyzes brand mentions on Reddit via public scraping"""

    def __init__(self, brand_name: str = "Rhone"):
        """Initialize Reddit analyzer

        Args:
            brand_name: Brand name to monitor (default: Rhone)
        """
        self.brand_name = brand_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; BrandSentimentAnalyzer/1.0)'
        }

    def search_subreddit(
        self,
        subreddit: str,
        query: str,
        time_filter: str = "month",
        limit: int = 25
    ) -> List[Dict]:
        """Search a specific subreddit for mentions

        Args:
            subreddit: Subreddit name (without r/)
            query: Search query
            time_filter: Time period (hour, day, week, month, year, all)
            limit: Maximum results (max 100 per request)

        Returns:
            List of post dictionaries
        """
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'relevance',
            't': time_filter,
            'limit': min(limit, 100)
        }

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                posts = []

                for child in data.get('data', {}).get('children', []):
                    post_data = child.get('data', {})

                    posts.append({
                        'type': 'submission',
                        'id': post_data.get('id'),
                        'subreddit': subreddit,
                        'title': post_data.get('title', ''),
                        'text': post_data.get('selftext', ''),
                        'author': post_data.get('author', '[deleted]'),
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': datetime.fromtimestamp(
                            post_data.get('created_utc', 0)
                        ).isoformat(),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'upvote_ratio': post_data.get('upvote_ratio', 0)
                    })

                return posts
            else:
                print(f"  Warning: Failed to fetch r/{subreddit} (status {response.status_code})")
                return []

        except Exception as e:
            print(f"  Error searching r/{subreddit}: {e}")
            return []

    def get_post_comments(self, post_url: str, brand_name: str) -> List[Dict]:
        """Get comments from a post that mention the brand

        Args:
            post_url: Reddit post permalink
            brand_name: Brand to search for in comments

        Returns:
            List of comment dictionaries mentioning the brand
        """
        # Convert permalink to JSON URL
        json_url = f"https://www.reddit.com{post_url}.json"

        try:
            response = requests.get(json_url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

            # Reddit returns [post_data, comments_data]
            if len(data) < 2:
                return []

            comments_data = data[1]
            brand_comments = []

            def extract_comments(comment_list, brand_lower):
                """Recursively extract comments that mention brand"""
                for item in comment_list.get('data', {}).get('children', []):
                    if item.get('kind') == 't1':  # Comment type
                        comment_data = item.get('data', {})
                        body = comment_data.get('body', '')

                        if brand_lower in body.lower():
                            brand_comments.append({
                                'type': 'comment',
                                'text': body,
                                'author': comment_data.get('author', '[deleted]'),
                                'score': comment_data.get('score', 0),
                                'created_utc': datetime.fromtimestamp(
                                    comment_data.get('created_utc', 0)
                                ).isoformat()
                            })

                        # Check replies
                        replies = comment_data.get('replies')
                        if replies and isinstance(replies, dict):
                            extract_comments(replies, brand_lower)

            extract_comments(comments_data, brand_name.lower())
            return brand_comments

        except Exception as e:
            return []

    def search_mentions(
        self,
        subreddits: Optional[List[str]] = None,
        time_filter: str = "month",
        limit_per_subreddit: int = 25,
        include_comments: bool = True
    ) -> List[Dict]:
        """Search for brand mentions across multiple subreddits

        Args:
            subreddits: List of subreddits to search (None = default list)
            time_filter: Time period (hour, day, week, month, year, all)
            limit_per_subreddit: Max results per subreddit
            include_comments: Whether to fetch comments mentioning brand

        Returns:
            List of mention dictionaries
        """
        # Default subreddits for activewear/fitness brands
        if subreddits is None:
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
                "buyitforlife",
                "onebag",
                "activewear",
                "advancedrunning",
                "ultrarunning",
                "ultralight",
                "backpacking",
                "weightlifting",
                "bodyweightfitness",
                "veganfitness",
                "xxfitness",
                "athleticwear",
                "techwear",
                "functionalfitness"
            ]

        all_mentions = []
        search_query = self.brand_name

        print(f"🔍 Searching for '{search_query}' mentions...")
        print(f"📅 Time period: {time_filter}")
        print(f"📊 Subreddits: {len(subreddits)}")
        if include_comments:
            print(f"💬 Including comments: Yes")
        print()

        for subreddit in subreddits:
            print(f"  Searching r/{subreddit}...", end=" ")

            posts = self.search_subreddit(
                subreddit,
                search_query,
                time_filter,
                limit_per_subreddit
            )

            if posts:
                all_mentions.extend(posts)
                print(f"✓ Found {len(posts)} posts", end="")

                # Get comments from each post
                if include_comments:
                    comments_found = 0
                    for post in posts:
                        time.sleep(1)  # Rate limiting
                        comments = self.get_post_comments(
                            post['url'].replace('https://reddit.com', ''),
                            self.brand_name
                        )
                        if comments:
                            for comment in comments:
                                comment['subreddit'] = post['subreddit']
                                comment['parent_post'] = post['title']
                                comment['url'] = post['url']
                                comment['num_comments'] = 0
                                comment['upvote_ratio'] = None
                                comment['title'] = f"Comment on: {post['title']}"
                            all_mentions.extend(comments)
                            comments_found += len(comments)

                    if comments_found > 0:
                        print(f" + {comments_found} comments")
                    else:
                        print()
            else:
                print("✗ No mentions found")

            # Rate limiting: Wait 2 seconds between subreddits
            time.sleep(2)

        print()
        print(f"✓ Total mentions found: {len(all_mentions)}")
        return all_mentions

    def analyze_sentiment_improved(self, text: str) -> Dict:
        """Improved sentiment analysis with negation handling

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment, confidence, and keywords
        """
        text_lower = text.lower()

        # Remove URLs to avoid false positives
        text_lower = re.sub(r'http\S+', '', text_lower)

        # Positive patterns and keywords
        positive_patterns = [
            r'\blove\b',
            r'\bgreat\b',
            r'\bamazing\b',
            r'\bexcellent\b',
            r'\bbest\b',
            r'\bperfect\b',
            r'\bcomfortable\b',
            r'\bquality\b',
            r'\brecommend\b',
            r'\bfavorite\b',
            r'\bawesome\b',
            r'\bworth\b',
            r'\bgood\b',
            r'\bsolid\b',
            r'\bnice\b',
            r'\bhappy\b',
            r'\bimpressed\b',
            r'\bfantastic\b',
            r'\boutstanding\b',
            r'\bsuperior\b',
            r'\bexceptional\b',
            r'\bgo-to\b',
            r'\bfan\b',
            r'\bhighly\srecommend\b'
        ]

        # Negative patterns and keywords
        negative_patterns = [
            r'\bhate\b',
            r'\bterrible\b',
            r'\bawful\b',
            r'\bworst\b',
            r'\bdisappointed\b',
            r'\buncomfortable\b',
            r'\bwaste\b',
            r'\boverpriced\b',
            r'\bbad\b',
            r'\bsucks\b',
            r'\bavoid\b',
            r'\bregret\b',
            r'\breturn\b',
            r'\bfell\sapart\b',
            r'\bhorrible\b',
            r'\btrash\b',
            r'\bgarbage\b',
            r'\buseless\b',
            r'\bdissatisfied\b',
            r'\bnot\sgood\b',
            r'\bnot\sgreat\b'
        ]

        # Negation words that flip sentiment
        negation_patterns = [
            r'\bnot\b',
            r'\bno\b',
            r'\bnever\b',
            r'\bwithout\b',
            r'\bdoesn\'t\b',
            r'\bdon\'t\b',
            r'\bwon\'t\b',
            r'\bcan\'t\b'
        ]

        # Check for negations near negative words (reduces false negatives)
        # e.g., "doesn't look cheap" should not be counted as negative
        text_sentences = text_lower.split('.')

        positive_score = 0
        negative_score = 0

        for sentence in text_sentences:
            # Check for negations in sentence
            has_negation = any(re.search(pattern, sentence) for pattern in negation_patterns)

            # Count positive patterns
            sentence_positive = sum(1 for pattern in positive_patterns if re.search(pattern, sentence))

            # Count negative patterns
            sentence_negative = sum(1 for pattern in negative_patterns if re.search(pattern, sentence))

            # If negation present, flip the scores for that sentence
            if has_negation and sentence_negative > 0:
                # Negation of negative = less negative
                sentence_negative = max(0, sentence_negative - 1)

            positive_score += sentence_positive
            negative_score += sentence_negative

        # Determine overall sentiment
        total_sentiment_words = positive_score + negative_score

        if positive_score > negative_score and positive_score > 0:
            sentiment = "Positive"
            confidence = min(positive_score / (total_sentiment_words + 1), 0.9)
        elif negative_score > positive_score and negative_score > 0:
            sentiment = "Negative"
            confidence = min(negative_score / (total_sentiment_words + 1), 0.9)
        else:
            sentiment = "Neutral"
            confidence = 0.5

        # Extract matched patterns (for debugging)
        matched_positive = [p.strip(r'\b') for p in positive_patterns if re.search(p, text_lower)]
        matched_negative = [p.strip(r'\b') for p in negative_patterns if re.search(p, text_lower)]

        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_score": positive_score,
            "negative_score": negative_score
        }

    def generate_report(
        self,
        subreddits: Optional[List[str]] = None,
        time_filter: str = "month",
        limit_per_subreddit: int = 25,
        include_comments: bool = True
    ) -> Dict:
        """Generate comprehensive sentiment report

        Args:
            subreddits: List of subreddits to search
            time_filter: Time period to analyze
            limit_per_subreddit: Max mentions per subreddit
            include_comments: Whether to include comment analysis

        Returns:
            Report dictionary with metrics and insights
        """
        # Get mentions
        mentions = self.search_mentions(
            subreddits,
            time_filter,
            limit_per_subreddit,
            include_comments
        )

        if not mentions:
            print("\n⚠️  No mentions found. Try:")
            print("  - Expanding the time period (e.g., 'year' instead of 'month')")
            print("  - Adding more subreddits")
            print("  - Checking different brand name variations")
            return {
                "brand": self.brand_name,
                "total_mentions": 0,
                "sentiment_distribution": {},
                "top_subreddits": [],
                "mentions": []
            }

        print(f"🔬 Analyzing sentiment...")

        # Analyze sentiment for each mention
        for mention in mentions:
            combined_text = f"{mention.get('title', '')} {mention.get('text', '')}"
            sentiment_result = self.analyze_sentiment_improved(combined_text)
            mention.update(sentiment_result)

        # Create DataFrame for analysis
        df = pd.DataFrame(mentions)

        # Sentiment distribution
        sentiment_dist = df["sentiment"].value_counts().to_dict()

        # Top subreddits by mention count
        top_subreddits = df["subreddit"].value_counts().head(10).to_dict()

        # Average scores by sentiment
        avg_scores = df.groupby("sentiment")["score"].mean().round(1).to_dict()

        # Time series (group by day)
        df["date"] = pd.to_datetime(df["created_utc"]).dt.date
        time_series = df.groupby("date").size().to_dict()
        time_series = {str(k): int(v) for k, v in time_series.items()}

        # Top positive and negative mentions
        positive_df = df[df["sentiment"] == "Positive"]
        negative_df = df[df["sentiment"] == "Negative"]

        top_positive_mentions = []
        if len(positive_df) > 0:
            top_positive_mentions = positive_df.nlargest(5, "score")[
                ["title", "subreddit", "score", "url"]
            ].to_dict("records")

        top_negative_mentions = []
        if len(negative_df) > 0:
            top_negative_mentions = negative_df.nlargest(5, "score")[
                ["title", "subreddit", "score", "url"]
            ].to_dict("records")

        # Type breakdown (posts vs comments)
        type_breakdown = df["type"].value_counts().to_dict() if "type" in df.columns else {}

        print(f"✓ Analysis complete!")
        print()

        return {
            "brand": self.brand_name,
            "time_period": time_filter,
            "generated_at": datetime.now().isoformat(),
            "total_mentions": len(mentions),
            "type_breakdown": type_breakdown,
            "sentiment_distribution": sentiment_dist,
            "avg_scores_by_sentiment": avg_scores,
            "top_subreddits": top_subreddits,
            "time_series": time_series,
            "top_positive_mentions": top_positive_mentions,
            "top_negative_mentions": top_negative_mentions,
            "all_mentions": mentions[:100]  # Limit to 100 for file size
        }


def save_report(report: Dict, output_file: str = "data/reddit_report.json"):
    """Save Reddit analysis report to file"""
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"💾 Report saved to: {output_file}")


if __name__ == "__main__":
    import sys

    # Allow brand name override
    brand = sys.argv[1] if len(sys.argv) > 1 else "Rhone"

    print("="*60)
    print(f"Reddit Sentiment Analysis: {brand}")
    print("="*60)
    print()

    # Create analyzer
    analyzer = RedditAnalyzer(brand)

    # Generate report (past year by default, including comments)
    report = analyzer.generate_report(
        time_filter="year",
        limit_per_subreddit=25,
        include_comments=True
    )

    # Display summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Brand: {report.get('brand', brand)}")
    print(f"Time Period: {report.get('time_period', 'year')}")
    print(f"Total Mentions: {report.get('total_mentions', 0)}")

    if report.get('type_breakdown'):
        print(f"\nMention Types:")
        for mtype, count in report['type_breakdown'].items():
            print(f"  {mtype}: {count}")

    print()

    if report['total_mentions'] > 0:
        print("Sentiment Distribution:")
        for sentiment, count in report['sentiment_distribution'].items():
            pct = (count / report['total_mentions'] * 100) if report['total_mentions'] > 0 else 0
            print(f"  {sentiment}: {count} ({pct:.1f}%)")
        print()

        print("Top Subreddits:")
        for subreddit, count in list(report['top_subreddits'].items())[:5]:
            print(f"  r/{subreddit}: {count} mentions")
        print()

    # Save report with brand-specific filename
    brand_lower = brand.lower().replace(' ', '_')
    output_file = f"data/{brand_lower}_reddit_report.json"
    save_report(report, output_file)

    print()
    print("✓ Done! View results in the Streamlit dashboard:")
    print("  streamlit run streamlit_app.py")
    print(f"  → Navigate to '{brand} Analysis' page")
