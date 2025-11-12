#!/usr/bin/env python3
"""
Create sample product data for testing the dashboard.
This simulates what the scraper would collect from Rhone.com.
"""

import json
from datetime import datetime
from pathlib import Path
import random


def generate_sample_data(num_products=100):
    """Generate sample product data"""

    categories = {
        "Men": ["Tops", "Bottoms", "Shorts", "Outerwear", "Accessories"],
        "Women": ["Tops", "Bottoms", "Leggings", "Sports Bras", "Outerwear"]
    }

    colors = [
        "Black", "White", "Navy", "Grey", "Charcoal", "Heather Grey",
        "Blue", "Red", "Green", "Olive", "Burgundy", "Tan", "Khaki",
        "Slate", "Steel Blue", "Forest Green", "Crimson"
    ]

    fabrics = [
        "Cotton", "Polyester", "Nylon", "Spandex", "Elastane",
        "Modal", "Bamboo", "Merino Wool", "Fleece", "Jersey"
    ]

    sizes = ["XS", "S", "M", "L", "XL", "XXL"]

    product_types = {
        "Tops": ["T-Shirt", "Long Sleeve", "Polo", "Henley", "Tank"],
        "Bottoms": ["Joggers", "Pants", "Chinos", "Sweatpants"],
        "Shorts": ["Athletic Shorts", "Running Shorts", "Casual Shorts"],
        "Outerwear": ["Jacket", "Hoodie", "Vest", "Pullover"],
        "Sports Bras": ["Sports Bra", "Training Bra"],
        "Leggings": ["Leggings", "Tights"],
        "Accessories": ["Hat", "Belt", "Socks"]
    }

    products = []

    for i in range(1, num_products + 1):
        gender = random.choice(list(categories.keys()))
        category = random.choice(categories[gender])

        product_type = random.choice(product_types.get(category, ["Item"]))
        color_name = random.choice(colors)

        name = f"{product_type} - {color_name}"

        # Select 1-3 colors
        num_colors = random.randint(1, 3)
        product_colors = random.sample(colors, num_colors)

        # Select 2-4 fabrics with percentages
        num_fabrics = random.randint(2, 4)
        product_fabrics = random.sample(fabrics, num_fabrics)
        fabric_percentages = [f"{random.randint(10, 80)}% {f}" for f in product_fabrics]

        # Price
        base_price = random.randint(40, 150)
        price = base_price + (base_price % 10)  # Round to nice numbers

        # 30% chance of sale
        sale_price = None
        if random.random() < 0.3:
            discount = random.randint(10, 30)
            sale_price = price * (1 - discount / 100)

        # 20% chance of best seller
        is_best_seller = random.random() < 0.2
        best_seller_rank = random.randint(1, 50) if is_best_seller else None

        # 10% chance of homepage product
        is_homepage = random.random() < 0.1

        product = {
            "product_id": f"rhone-{i:04d}",
            "name": name,
            "url": f"https://www.rhone.com/products/{name.lower().replace(' ', '-')}",
            "category": category,
            "subcategory": product_type,
            "gender": gender,
            "price": price,
            "sale_price": sale_price,
            "currency": "USD",
            "description": f"Premium {product_type.lower()} crafted with high-performance materials. Perfect for training, running, and everyday wear.",
            "colors": product_colors,
            "sizes": sizes,
            "fabrics": fabric_percentages,
            "best_seller_rank": best_seller_rank,
            "is_best_seller": is_best_seller,
            "images": [
                f"https://cdn.shopify.com/s/files/1/product{i}-1.jpg",
                f"https://cdn.shopify.com/s/files/1/product{i}-2.jpg",
            ],
            "scraped_at": datetime.now().isoformat(),
            "is_homepage_product": is_homepage,
            "sku": f"SKU-{i:06d}",
            "availability": random.choice(["In Stock", "In Stock", "In Stock", "Low Stock"])
        }

        products.append(product)

    return products


def main():
    """Generate and save sample data"""
    print("Generating sample product data...")

    products = generate_sample_data(100)

    # Save to data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    output_file = data_dir / f"rhone_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"\nGenerated {len(products)} sample products")
    print(f"Saved to: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Upload to Supabase: python database/upload_data.py")
    print(f"2. Run dashboard: python run.py dashboard")
    print(f"\nNote: This is sample data. To scrape real data from Rhone.com,")
    print(f"you'll need to handle their bot protection (see README for options).")


if __name__ == "__main__":
    main()
