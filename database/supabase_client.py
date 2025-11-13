import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Optional
import json

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class SupabaseClient:
    """Client for interacting with Supabase database"""

    def __init__(self):
        """Initialize Supabase client"""
        # Try to get from environment variables first (for local .env)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        # If not found and streamlit is available, try streamlit secrets
        if (not url or not key) and HAS_STREAMLIT:
            try:
                url = url or st.secrets["SUPABASE_URL"]
                key = key or st.secrets["SUPABASE_KEY"]
            except Exception as e:
                # If secrets don't exist, pass and show error below
                pass

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set. "
                "For local: Copy .env.example to .env and add your credentials. "
                "For Streamlit Cloud: Add secrets in app settings."
            )

        self.client: Client = create_client(url, key)

    def insert_product(self, product_data: Dict) -> Dict:
        """Insert a single product into the database"""
        # Convert lists to JSON for JSONB columns
        if "colors" in product_data and isinstance(product_data["colors"], list):
            product_data["colors"] = json.dumps(product_data["colors"])

        if "sizes" in product_data and isinstance(product_data["sizes"], list):
            product_data["sizes"] = json.dumps(product_data["sizes"])

        if "fabrics" in product_data and isinstance(product_data["fabrics"], list):
            product_data["fabrics"] = json.dumps(product_data["fabrics"])

        if "images" in product_data and isinstance(product_data["images"], list):
            product_data["images"] = json.dumps(product_data["images"])

        # Upsert product (insert or update if exists)
        response = self.client.table("products").upsert(
            product_data,
            on_conflict="product_id"
        ).execute()

        return response.data

    def insert_products_batch(self, products: List[Dict]) -> List[Dict]:
        """Insert multiple products into the database"""
        # Process each product individually to avoid conflicts within batch
        successful = []
        skipped_no_name = 0

        for product in products:
            # Skip products without a name (database has NOT NULL constraint)
            if not product.get('name'):
                skipped_no_name += 1
                continue

            # Convert lists to JSON for JSONB columns
            product_copy = product.copy()

            if "colors" in product_copy and isinstance(product_copy["colors"], list):
                product_copy["colors"] = json.dumps(product_copy["colors"])

            if "sizes" in product_copy and isinstance(product_copy["sizes"], list):
                product_copy["sizes"] = json.dumps(product_copy["sizes"])

            if "fabrics" in product_copy and isinstance(product_copy["fabrics"], list):
                product_copy["fabrics"] = json.dumps(product_copy["fabrics"])

            if "images" in product_copy and isinstance(product_copy["images"], list):
                product_copy["images"] = json.dumps(product_copy["images"])

            if "badges" in product_copy and isinstance(product_copy["badges"], list):
                product_copy["badges"] = json.dumps(product_copy["badges"])

            try:
                # Insert without upsert (will fail if duplicate)
                response = self.client.table("products").insert(product_copy).execute()
                successful.append(response.data)
            except Exception as e:
                # Skip duplicates silently
                if "duplicate" not in str(e).lower() and "unique" not in str(e).lower() and "null value" not in str(e).lower():
                    print(f"  Error inserting product {product.get('product_id', 'unknown')}: {e}")
                continue

        if skipped_no_name > 0:
            print(f"  Skipped {skipped_no_name} products without names")

        return successful

    def get_all_products(self) -> List[Dict]:
        """Retrieve all products from the database"""
        response = self.client.table("products").select("*").execute()
        return response.data

    def get_products_by_category(self, category: str) -> List[Dict]:
        """Retrieve products by category"""
        response = self.client.table("products").select("*").eq("category", category).execute()
        return response.data

    def get_products_by_gender(self, gender: str) -> List[Dict]:
        """Retrieve products by gender"""
        response = self.client.table("products").select("*").eq("gender", gender).execute()
        return response.data

    def get_best_sellers(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve best selling products"""
        query = self.client.table("products").select("*").eq("is_best_seller", True).order("best_seller_rank")

        if limit:
            query = query.limit(limit)

        response = query.execute()
        return response.data

    def get_homepage_products(self) -> List[Dict]:
        """Retrieve products featured on homepage"""
        response = self.client.table("products").select("*").eq("is_homepage_product", True).execute()
        return response.data

    def get_product_count(self) -> int:
        """Get total number of products"""
        response = self.client.table("products").select("id", count="exact").execute()
        return response.count

    def get_products_by_color(self, color: str) -> List[Dict]:
        """Retrieve products available in a specific color"""
        # Using JSONB contains operator
        response = self.client.table("products").select("*").filter(
            "colors", "cs", json.dumps([color])
        ).execute()
        return response.data

    def delete_all_products(self) -> None:
        """Delete all products from database (use with caution!)"""
        response = self.client.table("products").delete().neq("id", 0).execute()
        return response.data

    def execute_query(self, query: str) -> List[Dict]:
        """Execute a raw SQL query (for advanced analytics)"""
        response = self.client.rpc("execute_sql", {"query": query}).execute()
        return response.data
