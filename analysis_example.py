"""
Example analysis script showing how to use the Supabase client
for custom analytics and queries.

This demonstrates programmatic access to the product data
for advanced analysis beyond the dashboard.
"""

import sys
from pathlib import Path
import pandas as pd

# Add database module to path
sys.path.append(str(Path(__file__).parent / "database"))

from database.supabase_client import SupabaseClient


def main():
    """Run example analyses"""

    # Initialize client
    print("Connecting to Supabase...")
    client = SupabaseClient()

    # Example 1: Get total product count
    print("\n=== Example 1: Total Products ===")
    total = client.get_product_count()
    print(f"Total products in database: {total}")

    # Example 2: Get all products and convert to DataFrame
    print("\n=== Example 2: Load All Products ===")
    products = client.get_all_products()
    df = pd.DataFrame(products)
    print(f"Loaded {len(df)} products into DataFrame")
    print(f"Columns: {', '.join(df.columns.tolist())}")

    # Example 3: Best sellers analysis
    print("\n=== Example 3: Best Sellers ===")
    best_sellers = client.get_best_sellers(limit=10)
    if best_sellers:
        print(f"Top 10 best sellers:")
        for i, product in enumerate(best_sellers, 1):
            print(f"{i}. {product.get('name')} - {product.get('category')}")

    # Example 4: Products by gender
    print("\n=== Example 4: Products by Gender ===")
    mens_products = client.get_products_by_gender("Men")
    womens_products = client.get_products_by_gender("Women")
    print(f"Men's products: {len(mens_products)}")
    print(f"Women's products: {len(womens_products)}")

    # Example 5: Homepage products
    print("\n=== Example 5: Homepage Products ===")
    homepage = client.get_homepage_products()
    print(f"Products featured on homepage: {len(homepage)}")

    # Example 6: Products by category
    print("\n=== Example 6: Products by Category ===")
    if not df.empty and "category" in df.columns:
        category_counts = df["category"].value_counts()
        print("\nCategory distribution:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")

    # Example 7: Price analysis
    print("\n=== Example 7: Price Analysis ===")
    if not df.empty and "price" in df.columns:
        prices = df["price"].dropna()
        if len(prices) > 0:
            print(f"Average price: ${prices.mean():.2f}")
            print(f"Median price: ${prices.median():.2f}")
            print(f"Price range: ${prices.min():.2f} - ${prices.max():.2f}")

    # Example 8: Color analysis
    print("\n=== Example 8: Color Analysis ===")
    if not df.empty and "colors" in df.columns:
        # Flatten the colors list
        all_colors = []
        for colors in df["colors"].dropna():
            if isinstance(colors, list):
                all_colors.extend(colors)

        if all_colors:
            color_series = pd.Series(all_colors)
            top_colors = color_series.value_counts().head(5)
            print("Top 5 colors:")
            for color, count in top_colors.items():
                print(f"  {color}: {count} products")

    # Example 9: Fabric analysis
    print("\n=== Example 9: Fabric Analysis ===")
    if not df.empty and "fabrics" in df.columns:
        # Flatten the fabrics list
        all_fabrics = []
        for fabrics in df["fabrics"].dropna():
            if isinstance(fabrics, list):
                all_fabrics.extend(fabrics)

        if all_fabrics:
            unique_fabrics = len(set(all_fabrics))
            print(f"Unique fabrics used: {unique_fabrics}")

            fabric_series = pd.Series(all_fabrics)
            top_fabrics = fabric_series.value_counts().head(5)
            print("Top 5 fabrics:")
            for fabric, count in top_fabrics.items():
                print(f"  {fabric}: {count} mentions")

    # Example 10: Products with discounts
    print("\n=== Example 10: Discounted Products ===")
    if not df.empty and "price" in df.columns and "sale_price" in df.columns:
        discounted = df[df["sale_price"].notna()]
        print(f"Products on sale: {len(discounted)}")

        if len(discounted) > 0:
            discounted["discount_pct"] = (
                (discounted["price"] - discounted["sale_price"]) / discounted["price"] * 100
            )
            avg_discount = discounted["discount_pct"].mean()
            print(f"Average discount: {avg_discount:.1f}%")

    print("\n=== Analysis Complete ===")
    print("\nYou can modify this script to create your own custom analyses!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have:")
        print("1. Set up your .env file with Supabase credentials")
        print("2. Scraped and uploaded product data")
        print("\nRun: python run.py setup")
