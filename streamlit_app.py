import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
from pathlib import Path
import os
from anthropic import Anthropic

# Add database module to path
sys.path.append(str(Path(__file__).parent / "database"))

from database.supabase_client import SupabaseClient

# Page configuration
st.set_page_config(
    page_title="Rhone Product Analytics",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Modern, dense design inspired by Seattle Weather demo
st.markdown("""
<style>
    /* Reduce padding and margins for denser layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* Compact header */
    h1 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Compact metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }

    /* Remove extra spacing */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Compact dataframes */
    .dataframe {
        font-size: 0.85rem !important;
    }

    /* Cleaner tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }

    /* Reduce chart padding */
    .js-plotly-plot {
        margin-bottom: 0.5rem !important;
    }

    /* Divider styling */
    hr {
        margin: 1rem 0 !important;
    }

    /* Compact sidebar */
    section[data-testid="stSidebar"] {
        width: 250px !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data(brand_filter=None):
    """Load product data from Supabase

    Args:
        brand_filter: Optional brand name to filter (e.g., 'Rhone', 'Vuori')
    """
    try:
        client = SupabaseClient()
        products = client.get_all_products()

        if not products:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(products)

        # Filter by brand if specified
        if brand_filter and "brand" in df.columns:
            df = df[df["brand"] == brand_filter].copy()

        # Parse JSON fields
        for col in ["colors", "sizes", "fabrics", "images"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) else x)

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def display_overview(df):
    """Display overview metrics"""
    st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)

    # Calculate SKU counts (product-color combinations)
    def calculate_sku_count(dataframe):
        """Calculate total SKUs as product-color combinations"""
        total_skus = 0
        for _, row in dataframe.iterrows():
            if 'colors' in row and row['colors']:
                # Count each color as a separate SKU
                if isinstance(row['colors'], list):
                    total_skus += len(row['colors'])
                else:
                    total_skus += 1
            else:
                # Product with no colors counts as 1 SKU
                total_skus += 1
        return total_skus

    # Overall stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", len(df))

    with col2:
        categories = df["category"].nunique() if "category" in df.columns else 0
        st.metric("Categories", categories)

    with col3:
        mens_count = len(df[df["gender"] == "Men"]) if "gender" in df.columns else 0
        st.metric("Men's Products", mens_count)

    with col4:
        womens_count = len(df[df["gender"] == "Women"]) if "gender" in df.columns else 0
        st.metric("Women's Products", womens_count)

    # SKU counts row
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_skus = calculate_sku_count(df)
        st.metric("Total SKUs", total_skus, help="Each product-color combination counts as one SKU")

    with col2:
        if "gender" in df.columns:
            mens_df = df[df["gender"] == "Men"]
            mens_skus = calculate_sku_count(mens_df)
            st.metric("Men's SKUs", mens_skus, help="Men's product-color combinations")

    with col3:
        if "gender" in df.columns:
            womens_df = df[df["gender"] == "Women"]
            womens_skus = calculate_sku_count(womens_df)
            st.metric("Women's SKUs", womens_skus, help="Women's product-color combinations")

    # Gender breakdown
    st.markdown('<div class="section-header">👥 Products by Gender & Category</div>', unsafe_allow_html=True)

    if "gender" in df.columns and "category" in df.columns:
        # Create two columns for Men's and Women's
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Products")
            mens_df = df[df["gender"] == "Men"]

            if len(mens_df) > 0:
                mens_by_category = mens_df.groupby("category").size().sort_values(ascending=False)

                mens_category_df = pd.DataFrame({
                    'Category': mens_by_category.index,
                    'Count': mens_by_category.values,
                    'Percentage': (mens_by_category.values / len(mens_df) * 100).round(1)
                })

                # Pie chart
                fig = px.pie(
                    mens_category_df,
                    values='Count',
                    names='Category',
                    title="Men's Products by Category"
                )
                fig.update_traces(texttemplate='%{label}<br>%{value} (%{percent})')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 👗 Women's Products")
            womens_df = df[df["gender"] == "Women"]

            if len(womens_df) > 0:
                womens_by_category = womens_df.groupby("category").size().sort_values(ascending=False)

                womens_category_df = pd.DataFrame({
                    'Category': womens_by_category.index,
                    'Count': womens_by_category.values,
                    'Percentage': (womens_by_category.values / len(womens_df) * 100).round(1)
                })

                # Pie chart
                fig = px.pie(
                    womens_category_df,
                    values='Count',
                    names='Category',
                    title="Women's Products by Category"
                )
                fig.update_traces(texttemplate='%{label}<br>%{value} (%{percent})')
                st.plotly_chart(fig, use_container_width=True)


def display_category_analysis(df):
    """Display category analysis"""
    st.markdown('<div class="section-header">📊 Category Analysis</div>', unsafe_allow_html=True)

    if "category" not in df.columns:
        st.warning("Category data not available")
        return

    # Overall category distribution
    st.subheader("Overall Category Distribution")

    category_counts = df["category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title="Products per Category",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
        fig.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Add percentage
        category_counts["Percentage"] = (category_counts["Count"] / category_counts["Count"].sum() * 100).round(1)
        category_counts["Percentage"] = category_counts["Percentage"].apply(lambda x: f"{x}%")
        st.dataframe(
            category_counts,
            hide_index=True,
            use_container_width=True
        )

    st.divider()

    # Category breakdown by gender
    if "gender" in df.columns:
        st.subheader("Category Distribution by Gender")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Categories")
            mens_df = df[df["gender"] == "Men"]
            if len(mens_df) > 0:
                mens_categories = mens_df["category"].value_counts().reset_index()
                mens_categories.columns = ["Category", "Count"]
                mens_categories["Percentage"] = (mens_categories["Count"] / mens_categories["Count"].sum() * 100).round(1)
                mens_categories["Percentage"] = mens_categories["Percentage"].apply(lambda x: f"{x}%")

                fig = px.pie(
                    mens_categories,
                    values="Count",
                    names="Category",
                    title="Men's Products by Category"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(mens_categories, hide_index=True, use_container_width=True)
            else:
                st.info("No men's products found")

        with col2:
            st.markdown("### 👗 Women's Categories")
            womens_df = df[df["gender"] == "Women"]
            if len(womens_df) > 0:
                womens_categories = womens_df["category"].value_counts().reset_index()
                womens_categories.columns = ["Category", "Count"]
                womens_categories["Percentage"] = (womens_categories["Count"] / womens_categories["Count"].sum() * 100).round(1)
                womens_categories["Percentage"] = womens_categories["Percentage"].apply(lambda x: f"{x}%")

                fig = px.pie(
                    womens_categories,
                    values="Count",
                    names="Category",
                    title="Women's Products by Category"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(womens_categories, hide_index=True, use_container_width=True)
            else:
                st.info("No women's products found")

    st.divider()

    # Average prices by category
    if "price" in df.columns:
        st.subheader("Average Pricing by Category")

        pricing_by_category = df.groupby("category")["price"].agg(['mean', 'min', 'max', 'count']).reset_index()
        pricing_by_category.columns = ["Category", "Avg Price", "Min Price", "Max Price", "Product Count"]
        pricing_by_category = pricing_by_category.sort_values("Avg Price", ascending=False)

        # Format prices
        pricing_by_category["Avg Price"] = pricing_by_category["Avg Price"].apply(lambda x: f"${x:.2f}")
        pricing_by_category["Min Price"] = pricing_by_category["Min Price"].apply(lambda x: f"${x:.2f}")
        pricing_by_category["Max Price"] = pricing_by_category["Max Price"].apply(lambda x: f"${x:.2f}")

        st.dataframe(pricing_by_category, hide_index=True, use_container_width=True)

    st.divider()

    # Category details with filters
    st.subheader("Category Details")

    selected_category = st.selectbox(
        "Select Category to View Details",
        sorted(df["category"].unique())
    )

    category_df = df[df["category"] == selected_category]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", len(category_df))

    with col2:
        if "price" in category_df.columns:
            avg_price = category_df["price"].mean()
            st.metric("Avg Price", f"${avg_price:.2f}")

    with col3:
        if "gender" in category_df.columns:
            mens_count = len(category_df[category_df["gender"] == "Men"])
            st.metric("Men's Products", mens_count)

    with col4:
        if "gender" in category_df.columns:
            womens_count = len(category_df[category_df["gender"] == "Women"])
            st.metric("Women's Products", womens_count)

    # Show sample products from selected category
    st.markdown(f"### Sample Products from {selected_category}")

    # Get sample products
    sample_products = category_df.head(18)

    # Create card layout - 6 columns
    for i in range(0, len(sample_products), 6):
        cols = st.columns(6)
        for col_idx, col in enumerate(cols):
            product_idx = i + col_idx
            if product_idx < len(sample_products):
                product = sample_products.iloc[product_idx]

                with col:
                    # Display product image
                    if "images" in product and product["images"]:
                        # Parse images if it's a JSON string
                        images = product["images"]
                        if isinstance(images, str):
                            try:
                                images = json.loads(images)
                            except:
                                images = []

                        if images and len(images) > 0:
                            st.image(images[0], use_container_width=True)

                    # Product name
                    st.markdown(f"**{product['name']}**")

                    # Price info
                    price_text = ""
                    if "sale_price" in product and product["sale_price"] and product["sale_price"] != product.get("price"):
                        price_text = f"~~${product['price']:.2f}~~ **${product['sale_price']:.2f}**"
                    elif "price" in product and product["price"]:
                        price_text = f"**${product['price']:.2f}**"

                    if price_text:
                        st.markdown(price_text)

                    # Gender
                    if "gender" in product and product["gender"]:
                        st.caption(f"👤 {product['gender']}")

                    # Colors available
                    if "colors" in product and product["colors"]:
                        colors = product["colors"]
                        if isinstance(colors, str):
                            try:
                                colors = json.loads(colors)
                            except:
                                colors = []

                        if colors and isinstance(colors, list):
                            # Display color names
                            color_text = ", ".join(colors[:5])  # Show first 5 colors
                            if len(colors) > 5:
                                color_text += f" +{len(colors) - 5} more"
                            st.caption(f"🎨 {color_text}")

                    st.markdown("---")


def get_color_hex(color_name):
    """Map color names to hex values for visualization"""
    color_name_lower = str(color_name).lower()

    # Color mapping dictionary - maps common color names to hex codes
    color_map = {
        # Blacks and Grays
        'black': '#000000',
        'charcoal': '#36454F',
        'slate': '#708090',
        'gray': '#808080',
        'grey': '#808080',
        'silver': '#C0C0C0',
        'smoke': '#738276',

        # Whites and Creams
        'white': '#FFFFFF',
        'cream': '#FFFDD0',
        'ivory': '#FFFFF0',
        'bone': '#E3DAC9',
        'sand': '#C2B280',

        # Blues
        'navy': '#000080',
        'blue': '#0000FF',
        'cobalt': '#0047AB',
        'royal': '#4169E1',
        'sky': '#87CEEB',
        'teal': '#008080',
        'aqua': '#00FFFF',
        'turquoise': '#40E0D0',

        # Greens
        'green': '#008000',
        'olive': '#808000',
        'forest': '#228B22',
        'sage': '#9DC183',
        'mint': '#98FF98',
        'lime': '#00FF00',
        'emerald': '#50C878',

        # Reds and Pinks
        'red': '#FF0000',
        'maroon': '#800000',
        'burgundy': '#800020',
        'crimson': '#DC143C',
        'pink': '#FFC0CB',
        'rose': '#FF007F',
        'coral': '#FF7F50',

        # Oranges and Yellows
        'orange': '#FFA500',
        'rust': '#B7410E',
        'copper': '#B87333',
        'gold': '#FFD700',
        'yellow': '#FFFF00',
        'amber': '#FFBF00',
        'tan': '#D2B48C',
        'beige': '#F5F5DC',
        'camel': '#C19A6B',

        # Purples
        'purple': '#800080',
        'violet': '#8F00FF',
        'lavender': '#E6E6FA',
        'plum': '#DDA0DD',
        'mauve': '#E0B0FF',

        # Browns
        'brown': '#964B00',
        'chocolate': '#7B3F00',
        'coffee': '#6F4E37',
        'mocha': '#967969',
        'taupe': '#483C32',
    }

    # Try to find a match in the color map
    for color_key, hex_value in color_map.items():
        if color_key in color_name_lower:
            return hex_value

    # Default to a neutral gray if no match found
    return '#808080'


def display_color_analysis(df):
    """Display color analysis"""
    st.markdown('<div class="section-header">🎨 Color Analysis</div>', unsafe_allow_html=True)

    if "colors" not in df.columns:
        st.warning("Color data not available")
        return

    # Explode colors column
    colors_df = df.explode("colors")
    colors_df = colors_df[colors_df["colors"].notna()]

    if len(colors_df) == 0:
        st.warning("No color data available")
        return

    # Most common colors
    color_counts = colors_df["colors"].value_counts().head(20).reset_index()
    color_counts.columns = ["Color", "Count"]

    # Calculate percentage
    total_color_mentions = len(colors_df)
    color_counts["Percent"] = (color_counts["Count"] / total_color_mentions * 100).round(1)
    color_counts["Percent"] = color_counts["Percent"].apply(lambda x: f"{x}%")

    # Map colors to hex values
    color_counts["hex"] = color_counts["Color"].apply(get_color_hex)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            color_counts,
            x="Color",
            y="Count",
            title="Top 20 Most Common Colors",
            color="Color",
            color_discrete_map={row["Color"]: row["hex"] for _, row in color_counts.iterrows()}
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            color_counts[["Color", "Count", "Percent"]],
            hide_index=True,
            use_container_width=True
        )

    # Colors per category
    if "category" in df.columns:
        st.subheader("Colors by Category")

        category_colors = colors_df.groupby(["category", "colors"]).size().reset_index(name="count")
        category_colors = category_colors.sort_values("count", ascending=False)

        # Top 5 colors per category
        top_colors_per_category = category_colors.groupby("category").head(5)

        # Create color mapping for all unique colors
        unique_colors = top_colors_per_category["colors"].unique()
        color_discrete_map = {color: get_color_hex(color) for color in unique_colors}

        fig = px.bar(
            top_colors_per_category,
            x="category",
            y="count",
            color="colors",
            title="Top 5 Colors per Category",
            barmode="stack",
            color_discrete_map=color_discrete_map
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # Add visual representation of top colors by category
        st.markdown("#### Color Distribution by Category")

        # Create a pivot table showing top 3 colors per category
        category_breakdown = []
        for category in sorted(colors_df["category"].unique()):
            cat_colors = colors_df[colors_df["category"] == category]["colors"].value_counts().head(3)
            row = {"Category": category}
            for i, (color, count) in enumerate(cat_colors.items(), 1):
                row[f"#{i} Color"] = color
                row[f"#{i} Count"] = count
            category_breakdown.append(row)

        if category_breakdown:
            breakdown_df = pd.DataFrame(category_breakdown)

            # Fill missing values
            for i in range(1, 4):
                if f"#{i} Color" not in breakdown_df.columns:
                    breakdown_df[f"#{i} Color"] = "-"
                    breakdown_df[f"#{i} Count"] = 0
                else:
                    breakdown_df[f"#{i} Color"] = breakdown_df[f"#{i} Color"].fillna("-")
                    breakdown_df[f"#{i} Count"] = breakdown_df[f"#{i} Count"].fillna(0)

            # Create display dataframe with color chips using HTML
            def format_color_with_chip(color, count):
                if color == "-":
                    return "-"
                hex_color = get_color_hex(color)
                # Create a small colored square followed by the color name and count
                return f'<span style="display:inline-block;width:15px;height:15px;background-color:{hex_color};border:1px solid #ccc;margin-right:5px;vertical-align:middle;"></span>{color} ({int(count)})'

            display_df = pd.DataFrame({
                "Category": breakdown_df["Category"],
                "Top Color": breakdown_df.apply(lambda row: format_color_with_chip(row['#1 Color'], row['#1 Count']), axis=1),
                "2nd Color": breakdown_df.apply(lambda row: format_color_with_chip(row['#2 Color'], row['#2 Count']), axis=1),
                "3rd Color": breakdown_df.apply(lambda row: format_color_with_chip(row['#3 Color'], row['#3 Count']), axis=1),
            })

            # Display as HTML to render color chips
            st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Colors by gender
    if "gender" in df.columns:
        st.subheader("Colors by Gender")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Top Colors")
            mens_colors = colors_df[colors_df["gender"] == "Men"]
            if len(mens_colors) > 0:
                mens_color_counts = mens_colors["colors"].value_counts().head(10).reset_index()
                mens_color_counts.columns = ["Color", "Count"]

                # Calculate percentage
                total_mens_colors = len(mens_colors)
                mens_color_counts["Percent"] = (mens_color_counts["Count"] / total_mens_colors * 100).round(1)
                mens_color_counts["Percent"] = mens_color_counts["Percent"].apply(lambda x: f"{x}%")

                # Create color mapping
                color_discrete_map = {color: get_color_hex(color) for color in mens_color_counts["Color"]}

                fig = px.bar(
                    mens_color_counts,
                    x="Color",
                    y="Count",
                    title="Top 10 Colors in Men's Products",
                    color="Color",
                    color_discrete_map=color_discrete_map
                )
                fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
                fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(mens_color_counts[["Color", "Count", "Percent"]], hide_index=True, use_container_width=True)
            else:
                st.info("No men's color data available")

        with col2:
            st.markdown("### 👗 Women's Top Colors")
            womens_colors = colors_df[colors_df["gender"] == "Women"]
            if len(womens_colors) > 0:
                womens_color_counts = womens_colors["colors"].value_counts().head(10).reset_index()
                womens_color_counts.columns = ["Color", "Count"]

                # Calculate percentage
                total_womens_colors = len(womens_colors)
                womens_color_counts["Percent"] = (womens_color_counts["Count"] / total_womens_colors * 100).round(1)
                womens_color_counts["Percent"] = womens_color_counts["Percent"].apply(lambda x: f"{x}%")

                # Create color mapping
                color_discrete_map = {color: get_color_hex(color) for color in womens_color_counts["Color"]}

                fig = px.bar(
                    womens_color_counts,
                    x="Color",
                    y="Count",
                    title="Top 10 Colors in Women's Products",
                    color="Color",
                    color_discrete_map=color_discrete_map
                )
                fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
                fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(womens_color_counts[["Color", "Count", "Percent"]], hide_index=True, use_container_width=True)
            else:
                st.info("No women's color data available")


def display_fabric_analysis(df):
    """Display fabric analysis"""
    st.markdown('<div class="section-header">🧵 Fabric Analysis</div>', unsafe_allow_html=True)

    if "fabrics" not in df.columns:
        st.warning("Fabric data not available")
        return

    # Explode fabrics column
    fabrics_df = df.explode("fabrics")
    fabrics_df = fabrics_df[fabrics_df["fabrics"].notna()]

    if len(fabrics_df) == 0:
        st.warning("No fabric data available")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        unique_fabrics = fabrics_df["fabrics"].nunique()
        st.metric("Unique Fabrics", unique_fabrics)

    with col2:
        total_fabric_mentions = len(fabrics_df)
        st.metric("Total Fabric Mentions", total_fabric_mentions)

    with col3:
        avg_fabrics_per_product = len(fabrics_df) / len(df)
        st.metric("Avg Fabrics per Product", f"{avg_fabrics_per_product:.1f}")

    # Most common fabrics
    fabric_counts = fabrics_df["fabrics"].value_counts().head(15).reset_index()
    fabric_counts.columns = ["Fabric", "Count"]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            fabric_counts,
            x="Fabric",
            y="Count",
            title="Most Common Fabrics",
            color="Count",
            color_continuous_scale="Greens"
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            fabric_counts,
            hide_index=True,
            use_container_width=True
        )

    # Fabrics per category
    if "category" in df.columns:
        st.subheader("Fabrics by Category")

        category_fabrics = fabrics_df.groupby(["category", "fabrics"]).size().reset_index(name="count")
        category_fabrics = category_fabrics.sort_values("count", ascending=False)

        # Top 5 fabrics per category
        top_fabrics_per_category = category_fabrics.groupby("category").head(5)

        fig = px.bar(
            top_fabrics_per_category,
            x="category",
            y="count",
            color="fabrics",
            title="Top 5 Fabrics per Category",
            barmode="stack"
        )
        fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def display_best_sellers(df):
    """Display best sellers analysis"""
    st.markdown('<div class="section-header">⭐ Best Sellers Analysis</div>', unsafe_allow_html=True)

    if "is_best_seller" not in df.columns:
        st.warning("Best seller data not available")
        return

    best_sellers_df = df[df["is_best_seller"] == True].copy()

    if len(best_sellers_df) == 0:
        st.warning("No best sellers found in the data")
        return

    st.write(f"Total Best Sellers: **{len(best_sellers_df)}**")

    # Top 20 best sellers per gender
    if "gender" in df.columns:
        st.subheader("Top 20 Best Sellers by Gender")

        tabs = st.tabs(["Men", "Women", "All"])

        with tabs[0]:
            men_best = best_sellers_df[best_sellers_df["gender"] == "Men"].head(20)
            if len(men_best) > 0:
                display_best_seller_table(men_best)
            else:
                st.info("No men's best sellers found")

        with tabs[1]:
            women_best = best_sellers_df[best_sellers_df["gender"] == "Women"].head(20)
            if len(women_best) > 0:
                display_best_seller_table(women_best)
            else:
                st.info("No women's best sellers found")

        with tabs[2]:
            all_best = best_sellers_df.head(20)
            display_best_seller_table(all_best)

    # Top 5 best sellers per category
    if "category" in df.columns:
        st.subheader("Top 5 Best Sellers by Category")

        categories = best_sellers_df["category"].unique()

        for category in categories:
            if pd.notna(category):
                with st.expander(f"{category}"):
                    cat_best = best_sellers_df[best_sellers_df["category"] == category].head(5)
                    display_best_seller_table(cat_best)


def display_best_seller_table(df):
    """Display best seller products in a table"""
    display_cols = ["name", "category", "gender", "price", "sale_price", "colors", "url"]
    available_cols = [col for col in display_cols if col in df.columns]

    display_df = df[available_cols].copy()

    # Format prices
    if "price" in display_df.columns:
        display_df["price"] = display_df["price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")

    if "sale_price" in display_df.columns:
        display_df["sale_price"] = display_df["sale_price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")

    # Format colors as comma-separated string
    if "colors" in display_df.columns:
        display_df["colors"] = display_df["colors"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) and len(x) > 0 else "-"
        )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Product Link"),
            "price": "Regular Price",
            "sale_price": "Sale Price",
            "colors": "Available Colors"
        }
    )


def display_sales_analysis(df):
    """Display sales and pricing analysis"""
    st.markdown('<div class="section-header">🏷️ Sales & Pricing Analysis</div>', unsafe_allow_html=True)

    # Check if we have sale data
    has_sale_data = "on_sale" in df.columns or "sale_price" in df.columns

    if not has_sale_data:
        st.warning("Sale data not available in this dataset")
        return

    # Determine which products are on sale
    # A product is on sale if it has a sale_price value (not null/empty)
    # Products with only price (no sale_price) are considered full price items
    if "sale_price" in df.columns:
        on_sale_df = df[df["sale_price"].notna()]
        full_price_df = df[df["sale_price"].isna()]
    else:
        on_sale_df = pd.DataFrame()  # Empty dataframe if no sale_price column
        full_price_df = df.copy()  # All products are full price if no sale_price column

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Products on Sale", len(on_sale_df))

    with col2:
        sale_percentage = (len(on_sale_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("% on Sale", f"{sale_percentage:.1f}%")

    with col3:
        if "price" in full_price_df.columns and len(full_price_df) > 0:
            avg_full_price = full_price_df["price"].mean()
            st.metric("Avg Full Price (non-sale)", f"${avg_full_price:.2f}")

    with col4:
        if "sale_price" in on_sale_df.columns and len(on_sale_df) > 0:
            avg_sale = on_sale_df["sale_price"].mean()
            st.metric("Avg Sale Price", f"${avg_sale:.2f}")

    # Calculate discount percentages
    # Only show discount distribution for products with actual discounts (sale_price < price)
    if "price" in on_sale_df.columns and "sale_price" in on_sale_df.columns:
        discount_df = on_sale_df[
            on_sale_df["price"].notna() &
            on_sale_df["sale_price"].notna() &
            (on_sale_df["sale_price"] < on_sale_df["price"])
        ].copy()

        if len(discount_df) > 0:
            discount_df["discount_pct"] = (
                (discount_df["price"] - discount_df["sale_price"]) / discount_df["price"] * 100
            )

            st.subheader("Discount Distribution")

            col1, col2 = st.columns([2, 1])

            with col1:
                fig = px.histogram(
                    discount_df,
                    x="discount_pct",
                    nbins=20,
                    title="Distribution of Discount Percentages",
                    labels={"discount_pct": "Discount %", "count": "Number of Products"}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                avg_discount = discount_df["discount_pct"].mean()
                max_discount = discount_df["discount_pct"].max()
                min_discount = discount_df["discount_pct"].min()

                st.metric("Average Discount", f"{avg_discount:.1f}%")
                st.metric("Max Discount", f"{max_discount:.1f}%")
                st.metric("Min Discount", f"{min_discount:.1f}%")

    # Average pricing by category
    st.subheader("Average Pricing by Category")

    if "category" in df.columns and "price" in df.columns and "gender" in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Full Price Items
            st.markdown("#### Full Price Items")
            if len(full_price_df) > 0:
                # Get all categories
                all_categories = full_price_df["category"].unique()

                # Calculate averages by category and gender
                mens_full = full_price_df[full_price_df["gender"] == "Men"]
                womens_full = full_price_df[full_price_df["gender"] == "Women"]

                mens_avg = mens_full.groupby("category")["price"].mean() if len(mens_full) > 0 else pd.Series()
                womens_avg = womens_full.groupby("category")["price"].mean() if len(womens_full) > 0 else pd.Series()
                overall_avg = full_price_df.groupby("category")["price"].mean()

                # Create combined dataframe
                full_price_combined = pd.DataFrame({
                    "Category": overall_avg.index,
                    "Men": mens_avg.reindex(overall_avg.index),
                    "Women": womens_avg.reindex(overall_avg.index),
                    "Overall": overall_avg.values
                })

                # Format prices
                full_price_combined["Men"] = full_price_combined["Men"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                full_price_combined["Women"] = full_price_combined["Women"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                full_price_combined["Overall"] = full_price_combined["Overall"].apply(lambda x: f"${x:.2f}")

                st.dataframe(full_price_combined, hide_index=True, use_container_width=True)

        with col2:
            # Sale Items
            st.markdown("#### Sale Items")
            if len(on_sale_df) > 0 and "sale_price" in on_sale_df.columns:
                # Get all categories
                all_categories = on_sale_df["category"].unique()

                # Calculate averages by category and gender
                mens_sale = on_sale_df[on_sale_df["gender"] == "Men"]
                womens_sale = on_sale_df[on_sale_df["gender"] == "Women"]

                mens_avg = mens_sale.groupby("category")["sale_price"].mean() if len(mens_sale) > 0 else pd.Series()
                womens_avg = womens_sale.groupby("category")["sale_price"].mean() if len(womens_sale) > 0 else pd.Series()
                overall_avg = on_sale_df.groupby("category")["sale_price"].mean()

                # Create combined dataframe
                sale_price_combined = pd.DataFrame({
                    "Category": overall_avg.index,
                    "Men": mens_avg.reindex(overall_avg.index),
                    "Women": womens_avg.reindex(overall_avg.index),
                    "Overall": overall_avg.values
                })

                # Format prices
                sale_price_combined["Men"] = sale_price_combined["Men"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                sale_price_combined["Women"] = sale_price_combined["Women"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                sale_price_combined["Overall"] = sale_price_combined["Overall"].apply(lambda x: f"${x:.2f}")

                st.dataframe(sale_price_combined, hide_index=True, use_container_width=True)

    # Sales by gender and category
    if "category" in df.columns and "gender" in df.columns:
        st.subheader("Sale vs Full Price by Gender & Category")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Products")
            mens_df = df[df["gender"] == "Men"]
            if len(mens_df) > 0:
                mens_sales = on_sale_df[on_sale_df["gender"] == "Men"]
                mens_full = full_price_df[full_price_df["gender"] == "Men"]

                # Count by category
                mens_sale_counts = mens_sales.groupby("category").size().reset_index(name="On Sale")
                mens_full_counts = mens_full.groupby("category").size().reset_index(name="Full Price")

                # Merge the counts
                mens_combined = pd.merge(
                    mens_sale_counts,
                    mens_full_counts,
                    on="category",
                    how="outer"
                ).fillna(0)

                # Calculate total and percentage
                mens_combined["Total"] = mens_combined["On Sale"] + mens_combined["Full Price"]
                mens_combined["% On Sale"] = (mens_combined["On Sale"] / mens_combined["Total"] * 100).round(1)

                # Melt for stacked bar chart - reverse order so "On Sale" is on bottom
                mens_plot = mens_combined.melt(
                    id_vars=["category", "% On Sale", "Total"],
                    value_vars=["On Sale", "Full Price"],  # Reversed order
                    var_name="Type",
                    value_name="Count"
                )

                fig = px.bar(
                    mens_plot,
                    x="category",
                    y="Count",
                    color="Type",
                    title="Men's Products: Sale vs Full Price by Category",
                    barmode="stack",
                    color_discrete_map={"On Sale": "#FF6B6B", "Full Price": "#4ECDC4"}
                )
                fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))

                # Add percentage text annotations
                for idx, row in mens_combined.iterrows():
                    fig.add_annotation(
                        x=row["category"],
                        y=row["Total"],
                        text=f"{row['% On Sale']:.1f}%",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=11, color="black", family="Arial Black")
                    )

                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 👗 Women's Products")
            womens_df = df[df["gender"] == "Women"]
            if len(womens_df) > 0:
                womens_sales = on_sale_df[on_sale_df["gender"] == "Women"]
                womens_full = full_price_df[full_price_df["gender"] == "Women"]

                # Count by category
                womens_sale_counts = womens_sales.groupby("category").size().reset_index(name="On Sale")
                womens_full_counts = womens_full.groupby("category").size().reset_index(name="Full Price")

                # Merge the counts
                womens_combined = pd.merge(
                    womens_sale_counts,
                    womens_full_counts,
                    on="category",
                    how="outer"
                ).fillna(0)

                # Calculate total and percentage
                womens_combined["Total"] = womens_combined["On Sale"] + womens_combined["Full Price"]
                womens_combined["% On Sale"] = (womens_combined["On Sale"] / womens_combined["Total"] * 100).round(1)

                # Melt for stacked bar chart - reverse order so "On Sale" is on bottom
                womens_plot = womens_combined.melt(
                    id_vars=["category", "% On Sale", "Total"],
                    value_vars=["On Sale", "Full Price"],  # Reversed order
                    var_name="Type",
                    value_name="Count"
                )

                fig = px.bar(
                    womens_plot,
                    x="category",
                    y="Count",
                    color="Type",
                    title="Women's Products: Sale vs Full Price by Category",
                    barmode="stack",
                    color_discrete_map={"On Sale": "#FF6B6B", "Full Price": "#4ECDC4"}
                )
                fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))

                # Add percentage text annotations
                for idx, row in womens_combined.iterrows():
                    fig.add_annotation(
                        x=row["category"],
                        y=row["Total"],
                        text=f"{row['% On Sale']:.1f}%",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=11, color="black", family="Arial Black")
                    )

                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    # Sales by gender and color
    if "colors" in df.columns and "gender" in df.columns and len(on_sale_df) > 0:
        st.subheader("Sale Products by Gender & Color")

        # Explode colors for sale products only
        sale_colors_df = on_sale_df.explode("colors")
        sale_colors_df = sale_colors_df[sale_colors_df["colors"].notna()]

        if len(sale_colors_df) > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 👔 Men's Sale Products by Color")
                mens_sale_colors = sale_colors_df[sale_colors_df["gender"] == "Men"]
                if len(mens_sale_colors) > 0:
                    mens_color_sales = mens_sale_colors.groupby("colors").size().sort_values(ascending=False).head(10).reset_index()
                    mens_color_sales.columns = ["Color", "Count"]

                    # Create color mapping
                    color_discrete_map = {color: get_color_hex(color) for color in mens_color_sales["Color"]}

                    fig = px.bar(
                        mens_color_sales,
                        x="Color",
                        y="Count",
                        title="Top 10 Colors in Men's Sale Products",
                        color="Color",
                        color_discrete_map=color_discrete_map
                    )
                    fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
                    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No men's sale products with color data")

            with col2:
                st.markdown("### 👗 Women's Sale Products by Color")
                womens_sale_colors = sale_colors_df[sale_colors_df["gender"] == "Women"]
                if len(womens_sale_colors) > 0:
                    womens_color_sales = womens_sale_colors.groupby("colors").size().sort_values(ascending=False).head(10).reset_index()
                    womens_color_sales.columns = ["Color", "Count"]

                    # Create color mapping
                    color_discrete_map = {color: get_color_hex(color) for color in womens_color_sales["Color"]}

                    fig = px.bar(
                        womens_color_sales,
                        x="Color",
                        y="Count",
                        title="Top 10 Colors in Women's Sale Products",
                        color="Color",
                        color_discrete_map=color_discrete_map
                    )
                    fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.1)", width=1)))
                    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No women's sale products with color data")

    # Top sale items
    if len(on_sale_df) > 0:
        st.subheader("Current Sale Items")

        # Show products with biggest discounts
        if "price" in on_sale_df.columns and "sale_price" in on_sale_df.columns:
            sale_display = on_sale_df[on_sale_df["price"].notna() & on_sale_df["sale_price"].notna()].copy()
            sale_display["savings"] = sale_display["price"] - sale_display["sale_price"]
            sale_display["discount_pct"] = (sale_display["savings"] / sale_display["price"] * 100)

            sale_display = sale_display.sort_values("discount_pct", ascending=False).head(20)

            display_cols = ["name", "category", "price", "sale_price", "savings", "discount_pct", "colors"]
            available_cols = [col for col in display_cols if col in sale_display.columns]

            display_df = sale_display[available_cols].copy()
            display_df["price"] = display_df["price"].apply(lambda x: f"${x:.2f}")
            display_df["sale_price"] = display_df["sale_price"].apply(lambda x: f"${x:.2f}")
            display_df["savings"] = display_df["savings"].apply(lambda x: f"${x:.2f}")
            display_df["discount_pct"] = display_df["discount_pct"].apply(lambda x: f"{x:.1f}%")

            if "colors" in display_df.columns:
                display_df["colors"] = display_df["colors"].apply(
                    lambda x: ", ".join(x[:3]) if isinstance(x, list) and len(x) > 0 else "-"
                )

            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "price": "Regular",
                    "sale_price": "Sale",
                    "savings": "You Save",
                    "discount_pct": "Discount",
                    "colors": "Colors"
                }
            )


def display_homepage_analysis(df):
    """Display homepage products analysis"""
    st.markdown('<div class="section-header">🏠 Homepage Products Analysis</div>', unsafe_allow_html=True)

    if "is_homepage_product" not in df.columns:
        st.warning("Homepage product data not available")
        return

    homepage_df = df[df["is_homepage_product"] == True]

    if len(homepage_df) == 0:
        st.warning("No homepage products found in the data")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Products on Homepage", len(homepage_df))

    with col2:
        homepage_percent = (len(homepage_df) / len(df)) * 100
        st.metric("% of Total Products", f"{homepage_percent:.1f}%")

    # Homepage products by category
    if "category" in df.columns:
        st.subheader("Homepage Products by Category")

        category_counts = homepage_df["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]

        fig = px.pie(
            category_counts,
            values="Count",
            names="Category",
            title="Homepage Products Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    # List of homepage products
    st.subheader("Homepage Products")

    display_cols = ["name", "category", "gender", "price", "url"]
    available_cols = [col for col in display_cols if col in homepage_df.columns]

    if "price" in homepage_df.columns:
        display_df = homepage_df[available_cols].copy()
        display_df["price"] = display_df["price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
    else:
        display_df = homepage_df[available_cols]

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Product Link")
        }
    )


def display_line_plan(df):
    """Display strategic line plan analysis"""
    st.markdown('<div class="section-header">📋 Strategic Line Plan</div>', unsafe_allow_html=True)

    st.markdown("""
    This line plan provides strategic recommendations based on current product data analysis,
    including assortment balance, pricing strategy, and inventory optimization opportunities.
    """)

    # Executive Summary
    st.markdown("## Executive Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", len(df))

    with col2:
        if "gender" in df.columns:
            mens_count = len(df[df["gender"] == "Men"])
            st.metric("Men's Products", mens_count)

    with col3:
        if "gender" in df.columns:
            womens_count = len(df[df["gender"] == "Women"])
            st.metric("Women's Products", womens_count)

    with col4:
        if "category" in df.columns:
            category_count = df["category"].nunique()
            st.metric("Categories", category_count)

    st.divider()

    # Assortment Analysis
    st.markdown("## 📊 Assortment Analysis")

    if "category" in df.columns and "gender" in df.columns:
        # Category distribution by gender
        category_gender = df.groupby(["gender", "category"]).size().reset_index(name="count")

        # Calculate percentages within each gender
        mens_total = len(df[df["gender"] == "Men"])
        womens_total = len(df[df["gender"] == "Women"])

        category_gender["percentage"] = category_gender.apply(
            lambda row: (row["count"] / mens_total * 100) if row["gender"] == "Men" else (row["count"] / womens_total * 100),
            axis=1
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Assortment Mix")
            mens_assort = category_gender[category_gender["gender"] == "Men"].sort_values("count", ascending=False)
            mens_assort_display = mens_assort[["category", "count", "percentage"]].copy()
            mens_assort_display.columns = ["Category", "SKU Count", "% of Men's"]
            mens_assort_display["% of Men's"] = mens_assort_display["% of Men's"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(mens_assort_display, hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### 👗 Women's Assortment Mix")
            womens_assort = category_gender[category_gender["gender"] == "Women"].sort_values("count", ascending=False)
            womens_assort_display = womens_assort[["category", "count", "percentage"]].copy()
            womens_assort_display.columns = ["Category", "SKU Count", "% of Women's"]
            womens_assort_display["% of Women's"] = womens_assort_display["% of Women's"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(womens_assort_display, hide_index=True, use_container_width=True)

    st.divider()

    # Pricing Architecture
    st.markdown("## 💰 Pricing Architecture")

    if "price" in df.columns and "category" in df.columns and "gender" in df.columns:
        pricing_data = []

        for gender in ["Men", "Women"]:
            gender_df = df[df["gender"] == gender]
            for category in sorted(gender_df["category"].unique()):
                cat_df = gender_df[gender_df["category"] == category]
                cat_prices = cat_df["price"].dropna()

                if len(cat_prices) > 0:
                    pricing_data.append({
                        "Gender": gender,
                        "Category": category,
                        "SKU Count": len(cat_df),
                        "Avg Price": cat_prices.mean(),
                        "Min Price": cat_prices.min(),
                        "Max Price": cat_prices.max(),
                        "Price Range": cat_prices.max() - cat_prices.min()
                    })

        pricing_df = pd.DataFrame(pricing_data)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👔 Men's Price Points")
            mens_pricing = pricing_df[pricing_df["Gender"] == "Men"].copy()
            mens_pricing["Avg Price"] = mens_pricing["Avg Price"].apply(lambda x: f"${x:.2f}")
            mens_pricing["Min Price"] = mens_pricing["Min Price"].apply(lambda x: f"${x:.2f}")
            mens_pricing["Max Price"] = mens_pricing["Max Price"].apply(lambda x: f"${x:.2f}")
            mens_pricing["Price Range"] = mens_pricing["Price Range"].apply(lambda x: f"${x:.2f}")
            st.dataframe(mens_pricing[["Category", "SKU Count", "Avg Price", "Min Price", "Max Price"]],
                        hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### 👗 Women's Price Points")
            womens_pricing = pricing_df[pricing_df["Gender"] == "Women"].copy()
            womens_pricing["Avg Price"] = womens_pricing["Avg Price"].apply(lambda x: f"${x:.2f}")
            womens_pricing["Min Price"] = womens_pricing["Min Price"].apply(lambda x: f"${x:.2f}")
            womens_pricing["Max Price"] = womens_pricing["Max Price"].apply(lambda x: f"${x:.2f}")
            womens_pricing["Price Range"] = womens_pricing["Price Range"].apply(lambda x: f"${x:.2f}")
            st.dataframe(womens_pricing[["Category", "SKU Count", "Avg Price", "Min Price", "Max Price"]],
                        hide_index=True, use_container_width=True)

    st.divider()

    # Color Strategy
    st.markdown("## 🎨 Color Strategy")

    if "colors" in df.columns:
        colors_df = df.explode("colors")
        colors_df = colors_df[colors_df["colors"].notna()]

        if len(colors_df) > 0:
            st.markdown("### Core Color Palette")

            # Overall top colors
            top_colors = colors_df["colors"].value_counts().head(10).reset_index()
            top_colors.columns = ["Color", "SKU Count"]
            total_colors = len(colors_df)
            top_colors["% of Line"] = (top_colors["SKU Count"] / total_colors * 100).round(1)
            top_colors["% of Line"] = top_colors["% of Line"].apply(lambda x: f"{x:.1f}%")

            # Add color classification
            def classify_color(color_name):
                color_lower = str(color_name).lower()
                if any(x in color_lower for x in ['black', 'charcoal', 'navy', 'grey', 'gray']):
                    return 'Core Neutral'
                elif any(x in color_lower for x in ['white', 'cream', 'sand', 'bone']):
                    return 'Light Neutral'
                elif any(x in color_lower for x in ['blue', 'teal', 'aqua']):
                    return 'Cool Tone'
                elif any(x in color_lower for x in ['red', 'burgundy', 'crimson']):
                    return 'Warm Tone'
                elif any(x in color_lower for x in ['green', 'olive', 'sage']):
                    return 'Earth Tone'
                else:
                    return 'Seasonal/Fashion'

            top_colors["Color Family"] = top_colors["Color"].apply(classify_color)

            st.dataframe(top_colors, hide_index=True, use_container_width=True)

            # Color family distribution
            st.markdown("### Color Family Distribution")
            color_family_counts = top_colors.groupby("Color Family")["SKU Count"].sum().sort_values(ascending=False).reset_index()

            fig = px.pie(
                color_family_counts,
                values="SKU Count",
                names="Color Family",
                title="Product Distribution by Color Family"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Sales Performance & Opportunities
    st.markdown("## 📈 Sales Performance & Opportunities")

    if "sale_price" in df.columns:
        on_sale_df = df[df["sale_price"].notna()]
        full_price_df = df[df["sale_price"].isna()]

        col1, col2, col3 = st.columns(3)

        with col1:
            sale_pct = (len(on_sale_df) / len(df) * 100)
            st.metric("Products on Sale", f"{sale_pct:.1f}%")

        with col2:
            if len(full_price_df) > 0 and "price" in full_price_df.columns:
                avg_full = full_price_df["price"].mean()
                st.metric("Avg Full Price", f"${avg_full:.2f}")

        with col3:
            if len(on_sale_df) > 0 and "sale_price" in on_sale_df.columns:
                avg_sale = on_sale_df["sale_price"].mean()
                st.metric("Avg Sale Price", f"${avg_sale:.2f}")

        # Categories with highest discount rates
        if "category" in df.columns and len(on_sale_df) > 0:
            st.markdown("### Categories on Promotion")

            category_sale_analysis = []
            for category in df["category"].unique():
                cat_total = len(df[df["category"] == category])
                cat_sale = len(on_sale_df[on_sale_df["category"] == category])
                sale_pct = (cat_sale / cat_total * 100) if cat_total > 0 else 0

                category_sale_analysis.append({
                    "Category": category,
                    "Total SKUs": cat_total,
                    "On Sale": cat_sale,
                    "% On Sale": sale_pct
                })

            sale_analysis_df = pd.DataFrame(category_sale_analysis).sort_values("% On Sale", ascending=False)
            sale_analysis_df["% On Sale"] = sale_analysis_df["% On Sale"].apply(lambda x: f"{x:.1f}%")

            st.dataframe(sale_analysis_df, hide_index=True, use_container_width=True)

    st.divider()

    # Strategic Recommendations - CONSOLIDATED
    st.markdown("## 💡 Key Strategic Insights")

    # Collect insights data
    insights = []

    # Gender balance
    if "gender" in df.columns:
        mens_pct = (len(df[df["gender"] == "Men"]) / len(df) * 100)
        womens_pct = (len(df[df["gender"] == "Women"]) / len(df) * 100)

        if womens_pct > mens_pct * 1.5 or mens_pct > womens_pct * 1.5:
            status = "⚠️ Imbalanced"
            action = "Expand underrepresented gender"
        else:
            status = "✓ Balanced"
            action = "Maintain current mix"

        insights.append({
            "Area": "Gender Mix",
            "Current State": f"{mens_pct:.0f}% Men's / {womens_pct:.0f}% Women's",
            "Status": status,
            "Action": action
        })

    # Promotional intensity
    if "sale_price" in df.columns:
        on_sale_df = df[df["sale_price"].notna()]
        sale_pct = (len(on_sale_df) / len(df) * 100)

        if sale_pct > 40:
            status = "🔴 Critical"
            action = "Reduce markdowns, improve inventory planning"
        elif sale_pct > 25:
            status = "⚠️ Elevated"
            action = "Monitor patterns, adjust buying"
        elif sale_pct < 15:
            status = "⚠️ Low"
            action = "Add strategic promotions for velocity"
        else:
            status = "✓ Healthy"
            action = "Maintain 15-25% range"

        insights.append({
            "Area": "Promotional Rate",
            "Current State": f"{sale_pct:.0f}% on sale",
            "Status": status,
            "Action": action
        })

    # Category concentration
    if "category" in df.columns:
        category_dist = df["category"].value_counts()
        top_category = category_dist.index[0]
        top_category_pct = (category_dist.iloc[0] / len(df) * 100)

        if top_category_pct > 40:
            status = "⚠️ High Risk"
            action = "Diversify categories"
        elif top_category_pct > 30:
            status = "⚠️ Monitor"
            action = "Watch concentration levels"
        else:
            status = "✓ Diversified"
            action = "Maintain balance"

        insights.append({
            "Area": "Category Mix",
            "Current State": f"{top_category}: {top_category_pct:.0f}%",
            "Status": status,
            "Action": action
        })

    # Color diversity
    if "colors" in df.columns:
        colors_df_temp = df.explode("colors")
        colors_df_temp = colors_df_temp[colors_df_temp["colors"].notna()]
        if len(colors_df_temp) > 0:
            color_dist = colors_df_temp["colors"].value_counts()
            top_color = color_dist.index[0]
            top_color_pct = (color_dist.iloc[0] / len(colors_df_temp) * 100)
            total_colors = len(color_dist)

            if top_color_pct > 25:
                status = "⚠️ Concentrated"
                action = "Expand color palette"
            elif top_color_pct > 20:
                status = "⚠️ Monitor"
                action = "Add fashion colors"
            else:
                status = "✓ Balanced"
                action = "Maintain 60/40 neutral/color"

            insights.append({
                "Area": "Color Strategy",
                "Current State": f"{top_color}: {top_color_pct:.0f}% ({total_colors} total)",
                "Status": status,
                "Action": action
            })

    # SKU count
    total_skus = len(df)
    if total_skus > 800:
        status = "⚠️ Bloated"
        action = "Rationalize to 600-700 SKUs"
    elif total_skus < 400:
        status = "⚠️ Limited"
        action = "Expand in top categories"
    else:
        status = "✓ Optimal"
        action = "Maintain efficient range"

    insights.append({
        "Area": "SKU Count",
        "Current State": f"{total_skus} total SKUs",
        "Status": status,
        "Action": action
    })

    # Display as compact table
    if insights:
        insights_df = pd.DataFrame(insights)
        st.dataframe(
            insights_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Area": st.column_config.TextColumn("Area", width="small"),
                "Current State": st.column_config.TextColumn("Current State", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Action": st.column_config.TextColumn("Recommended Action", width="large")
            }
        )

    # Add cadence strategy callout
    st.markdown("### 📦 Product Cadence Strategy")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        **Core Basics** (25%)
        - ~{int(total_skus * 0.25)} SKUs
        - Always available
        - 4-5 neutral colors
        - Minimal discounts
        """)

    with col2:
        st.markdown("""
        **Monthly Drops** (45%)
        - 15-25 SKUs/month
        - 8-12 week lifecycle
        - Test & react model
        - Trend colors
        """)

    with col3:
        st.markdown("""
        **Seasonal Collections** (30%)
        - 4 major drops/year
        - 50-90 SKUs each
        - Cohesive stories
        - 60-70% full price target
        """)

    st.divider()

    # Proposed Product Drop Schedule
    st.markdown("## 📅 Proposed Annual Drop Schedule")

    st.markdown("""
    Below is a recommended 12-month product cadence combining basics, monthly newness drops,
    and seasonal collections to maintain customer engagement while optimizing inventory turns.
    """)

    # Create schedule dataframe
    schedule_data = [
        {
            "Month": "January",
            "Drop Type": "Monthly Drop",
            "Theme": "New Year Resolution / Performance",
            "Focus Categories": "Performance Tops, Bottoms, Accessories",
            "SKU Count": "15-20",
            "Color Strategy": "Core neutrals + 1-2 motivational brights"
        },
        {
            "Month": "February",
            "Drop Type": "SPRING COLLECTION",
            "Theme": "Spring Awakening / Transition",
            "Focus Categories": "Lightweight Outerwear, Transition Tops, Bright Bottoms",
            "SKU Count": "60-75",
            "Color Strategy": "Fresh pastels, bright greens, sky blues, coral"
        },
        {
            "Month": "March",
            "Drop Type": "Monthly Drop",
            "Theme": "Spring Training / Active Lifestyle",
            "Focus Categories": "Running Shorts, Breathable Tops, Light Jackets",
            "SKU Count": "18-25",
            "Color Strategy": "Energy colors: orange, lime, aqua"
        },
        {
            "Month": "April",
            "Drop Type": "Monthly Drop",
            "Theme": "Earth Day / Sustainable Performance",
            "Focus Categories": "Eco-friendly fabrics, Versatile Basics",
            "SKU Count": "15-20",
            "Color Strategy": "Earth tones: sage, sand, terracotta"
        },
        {
            "Month": "May",
            "Drop Type": "SUMMER COLLECTION",
            "Theme": "Summer Heat / Maximum Performance",
            "Focus Categories": "Performance Shorts, Tank Tops, Swim",
            "SKU Count": "50-60",
            "Color Strategy": "Vibrant summer: royal blue, sunset orange, tropical prints"
        },
        {
            "Month": "June",
            "Drop Type": "Monthly Drop",
            "Theme": "Summer Essentials / Travel Ready",
            "Focus Categories": "Quick-dry Shorts, Packable Tops, Accessories",
            "SKU Count": "15-20",
            "Color Strategy": "Navy, white, chambray - travel friendly"
        },
        {
            "Month": "July",
            "Drop Type": "Monthly Drop",
            "Theme": "Independence / Americana",
            "Focus Categories": "Patriotic colorways, Summer Basics",
            "SKU Count": "12-18",
            "Color Strategy": "Red, navy, white combinations"
        },
        {
            "Month": "August",
            "Drop Type": "FALL COLLECTION",
            "Theme": "Back to Routine / Fall Layering",
            "Focus Categories": "Hoodies, Long-sleeve Tops, Performance Joggers, Vests",
            "SKU Count": "75-90",
            "Color Strategy": "Autumn palette: burgundy, forest, charcoal, rust"
        },
        {
            "Month": "September",
            "Drop Type": "Monthly Drop",
            "Theme": "Fall Fitness / New Season Energy",
            "Focus Categories": "Transition Outerwear, Training Bottoms",
            "SKU Count": "20-25",
            "Color Strategy": "Rich jewel tones: emerald, sapphire, garnet"
        },
        {
            "Month": "October",
            "Drop Type": "Monthly Drop",
            "Theme": "Cozy Performance / Cold Weather Prep",
            "Focus Categories": "Fleece Layers, Thermal Tops, Winter Accessories",
            "SKU Count": "18-22",
            "Color Strategy": "Deep neutrals: black, charcoal, coffee"
        },
        {
            "Month": "November",
            "Drop Type": "HOLIDAY COLLECTION",
            "Theme": "Gift Season / Premium Performance",
            "Focus Categories": "Premium Hoodies, Gift Sets, Party Athleisure",
            "SKU Count": "50-65",
            "Color Strategy": "Gift-worthy: metallics, deep reds, premium blacks"
        },
        {
            "Month": "December",
            "Drop Type": "Monthly Drop",
            "Theme": "Winter Wellness / Cold Weather Essentials",
            "Focus Categories": "Base Layers, Insulated Outerwear, Recovery Wear",
            "SKU Count": "15-20",
            "Color Strategy": "Winter whites, icy blues, charcoal"
        }
    ]

    schedule_df = pd.DataFrame(schedule_data)

    # Display as formatted table with better column widths
    st.dataframe(
        schedule_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Month": st.column_config.TextColumn("Month", width="small"),
            "Drop Type": st.column_config.TextColumn("Drop Type", width="medium"),
            "Theme": st.column_config.TextColumn("Theme", width="medium"),
            "Focus Categories": st.column_config.TextColumn("Focus Categories", width="large"),
            "SKU Count": st.column_config.TextColumn("SKU Count", width="small"),
            "Color Strategy": st.column_config.TextColumn("Color Strategy", width="large")
        },
        height=500
    )

    st.divider()

    # Proposed Assortment Mix
    st.markdown("## 🎯 Proposed Assortment Mix by Product Tier")

    st.markdown("""
    Based on the recommended cadence strategy, here's how the product line should be structured
    across Basics, Monthly Drops, and Seasonal Collections:
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Men's Assortment Structure")

        mens_structure = pd.DataFrame({
            "Product Tier": ["Core Basics (Year-round)", "Monthly Drops (Rotating)", "Seasonal Collections", "Clearance/Transition"],
            "Category Mix": [
                "Tees (40%), Shorts (30%), Bottoms (20%), Basics (10%)",
                "Trend Tops (35%), Seasonal Bottoms (30%), Outerwear (25%), Accessories (10%)",
                "Outerwear (40%), Seasonal Tops (30%), Bottoms (20%), Special Items (10%)",
                "Prior season across all categories"
            ],
            "SKU Count": [f"{int(mens_count * 0.25)}", f"{int(mens_count * 0.45)}", f"{int(mens_count * 0.20)}", f"{int(mens_count * 0.10)}"],
            "Color Depth": ["4-5 core neutrals", "6-8 seasonal colors", "5-7 seasonal colors", "Limited - closeout only"],
            "Lifecycle": ["Always available", "8-12 weeks", "12-16 weeks", "4-8 weeks"],
            "Discount Strategy": ["Minimal (10-15% max)", "Test & react (20-30%)", "Controlled (25-40%)", "Aggressive (40-60%)"]
        }) if "gender" in df.columns else pd.DataFrame()

        st.dataframe(mens_structure, hide_index=True, use_container_width=True, height=250)

    with col2:
        st.markdown("### Women's Assortment Structure")

        womens_structure = pd.DataFrame({
            "Product Tier": ["Core Basics (Year-round)", "Monthly Drops (Rotating)", "Seasonal Collections", "Clearance/Transition"],
            "Category Mix": [
                "Tops (35%), Leggings (35%), Sports Bras (20%), Basics (10%)",
                "Fashion Tops (30%), Seasonal Leggings (25%), Outerwear (25%), Accessories (20%)",
                "Outerwear (35%), Seasonal Tops (30%), Bottoms (25%), Special Items (10%)",
                "Prior season across all categories"
            ],
            "SKU Count": [f"{int(womens_count * 0.25)}", f"{int(womens_count * 0.45)}", f"{int(womens_count * 0.20)}", f"{int(womens_count * 0.10)}"],
            "Color Depth": ["4-5 core neutrals", "8-10 seasonal colors", "6-8 seasonal colors", "Limited - closeout only"],
            "Lifecycle": ["Always available", "8-12 weeks", "12-16 weeks", "4-8 weeks"],
            "Discount Strategy": ["Minimal (10-15% max)", "Test & react (20-30%)", "Controlled (25-40%)", "Aggressive (40-60%)"]
        }) if "gender" in df.columns else pd.DataFrame()

        st.dataframe(womens_structure, hide_index=True, use_container_width=True, height=250)

    st.markdown("---")

    # Summary metrics
    st.markdown("### Key Assortment Principles")

    principles_col1, principles_col2, principles_col3 = st.columns(3)

    with principles_col1:
        st.markdown("""
        **Inventory Allocation:**
        - Basics: 50-55% of $ inventory
        - Monthly Drops: 25-30% of $ inventory
        - Seasonal: 20-25% of $ inventory
        - Never exceed 100% total planned inventory
        """)

    with principles_col2:
        st.markdown("""
        **Markdown Cadence:**
        - Basics: End of season only (2x/year)
        - Monthly: Quick react (4-6 weeks)
        - Seasonal: Structured (8-12 weeks)
        - Target 60-70% full price sell-through
        """)

    with principles_col3:
        st.markdown("""
        **Color Strategy:**
        - Basics: 4-5 core neutrals always
        - Monthly: 2-3 trend colors rotating
        - Seasonal: 5-8 coordinated palette
        - Maintain 60% neutral / 40% color overall
        """)


def display_drop_schedule(df):
    """Display detailed annual drop schedule with gender breakdowns"""
    st.markdown('<div class="section-header">📅 Annual Drop Schedule</div>', unsafe_allow_html=True)

    st.markdown("""
    Comprehensive 12-month product cadence plan with detailed assortment breakdowns by gender.
    This schedule combines basics replenishment, monthly newness drops, and seasonal collections
    to maintain customer engagement while optimizing inventory turns and margin.
    """)

    # Get current totals by gender
    mens_count = len(df[df["gender"] == "Men"]) if "gender" in df.columns else 0
    womens_count = len(df[df["gender"] == "Women"]) if "gender" in df.columns else 0
    total_count = len(df)

    # Summary metrics
    st.markdown("## 📊 Annual Drop Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Annual Drops", "12 Monthly + 4 Seasonal")
    with col2:
        st.metric("Estimated New SKUs/Year", "350-450")
    with col3:
        st.metric("Core Basics (Year-round)", f"{int(total_count * 0.25)} SKUs")
    with col4:
        st.metric("Rotation SKUs", f"{int(total_count * 0.75)} SKUs")

    st.divider()

    # Month selector for detailed view
    st.markdown("## 📆 Monthly Drop Details")

    # Define monthly drop data with gender-specific breakdowns
    drops = {
        "January": {
            "type": "Monthly Drop",
            "theme": "New Year Resolution / Performance",
            "total_skus": "15-20",
            "color_strategy": "Core neutrals + 1-2 motivational brights (electric blue, lime green)",
            "mens": {
                "sku_count": "10-12",
                "categories": {
                    "Tops": {"count": "4-5", "details": "Performance tees, long-sleeve training tops"},
                    "Bottoms": {"count": "3-4", "details": "Training joggers, performance shorts"},
                    "Accessories": {"count": "2-3", "details": "Beanies, training gloves, water bottles"}
                },
                "colors": ["Black", "Charcoal", "Navy", "Electric Blue"],
                "price_points": "$48-$98",
                "key_fabrics": "GoldFusion, Silvertech"
            },
            "womens": {
                "sku_count": "5-8",
                "categories": {
                    "Tops": {"count": "2-3", "details": "Performance tanks, long-sleeve training tops"},
                    "Bottoms": {"count": "2-3", "details": "High-waist leggings, training shorts"},
                    "Accessories": {"count": "1-2", "details": "Headbands, training socks"}
                },
                "colors": ["Black", "Charcoal", "Navy", "Lime Green"],
                "price_points": "$48-$88",
                "key_fabrics": "GoldFusion, Silvertech"
            }
        },
        "February": {
            "type": "SPRING COLLECTION",
            "theme": "Spring Awakening / Transition",
            "total_skus": "60-75",
            "color_strategy": "Fresh pastels, bright greens, sky blues, coral, sand",
            "mens": {
                "sku_count": "35-42",
                "categories": {
                    "Outerwear": {"count": "8-10", "details": "Lightweight jackets, windbreakers, vests"},
                    "Tops": {"count": "12-15", "details": "Spring tees, quarter-zips, polo shirts"},
                    "Bottoms": {"count": "10-12", "details": "Chino shorts, performance pants, joggers"},
                    "Accessories": {"count": "5-6", "details": "Hats, bags, sunglasses"}
                },
                "colors": ["Navy", "Sky Blue", "Sage Green", "Sand", "White", "Coral"],
                "price_points": "$58-$178",
                "key_fabrics": "Cotton blends, lightweight performance fabrics"
            },
            "womens": {
                "sku_count": "25-33",
                "categories": {
                    "Outerwear": {"count": "6-8", "details": "Lightweight jackets, windbreakers"},
                    "Tops": {"count": "10-12", "details": "Spring tanks, tees, long-sleeves"},
                    "Bottoms": {"count": "7-9", "details": "Leggings, bike shorts, joggers"},
                    "Accessories": {"count": "2-4", "details": "Bags, headbands, sunglasses"}
                },
                "colors": ["Sky Blue", "Coral", "Sage Green", "Sand", "White", "Lavender"],
                "price_points": "$48-$158",
                "key_fabrics": "Lightweight performance, soft cotton blends"
            }
        },
        "March": {
            "type": "Monthly Drop",
            "theme": "Spring Training / Active Lifestyle",
            "total_skus": "18-25",
            "color_strategy": "Energy colors: orange, lime, aqua, bright coral",
            "mens": {
                "sku_count": "12-16",
                "categories": {
                    "Tops": {"count": "5-7", "details": "Running tees, breathable tanks"},
                    "Bottoms": {"count": "5-7", "details": "Running shorts, 7\" performance shorts"},
                    "Outerwear": {"count": "2-3", "details": "Light running jackets"}
                },
                "colors": ["Black", "Aqua", "Orange", "Lime"],
                "price_points": "$48-$128",
                "key_fabrics": "Lightweight, moisture-wicking"
            },
            "womens": {
                "sku_count": "6-9",
                "categories": {
                    "Tops": {"count": "3-4", "details": "Running tanks, breathable tees"},
                    "Bottoms": {"count": "2-3", "details": "Running shorts, capri leggings"},
                    "Sports Bras": {"count": "1-2", "details": "High-impact sports bras"}
                },
                "colors": ["Black", "Coral", "Aqua", "Lime"],
                "price_points": "$48-$118",
                "key_fabrics": "Lightweight, moisture-wicking"
            }
        },
        "April": {
            "type": "Monthly Drop",
            "theme": "Earth Day / Sustainable Performance",
            "total_skus": "15-20",
            "color_strategy": "Earth tones: sage, sand, terracotta, olive, natural",
            "mens": {
                "sku_count": "10-13",
                "categories": {
                    "Tops": {"count": "5-7", "details": "Organic cotton tees, recycled poly tanks"},
                    "Bottoms": {"count": "3-4", "details": "Sustainable joggers, eco shorts"},
                    "Accessories": {"count": "2", "details": "Recycled bags, organic beanies"}
                },
                "colors": ["Sage", "Sand", "Terracotta", "Olive"],
                "price_points": "$58-$98",
                "key_fabrics": "Organic cotton, recycled polyester"
            },
            "womens": {
                "sku_count": "5-7",
                "categories": {
                    "Tops": {"count": "2-3", "details": "Organic cotton tees, recycled tanks"},
                    "Bottoms": {"count": "2-3", "details": "Sustainable leggings, eco joggers"},
                    "Accessories": {"count": "1", "details": "Recycled bags"}
                },
                "colors": ["Sage", "Sand", "Terracotta", "Natural"],
                "price_points": "$48-$88",
                "key_fabrics": "Organic cotton, recycled polyester"
            }
        },
        "May": {
            "type": "SUMMER COLLECTION",
            "theme": "Summer Heat / Maximum Performance",
            "total_skus": "50-60",
            "color_strategy": "Vibrant summer: royal blue, sunset orange, white, tropical prints",
            "mens": {
                "sku_count": "30-36",
                "categories": {
                    "Tops": {"count": "12-15", "details": "Performance tanks, breathable tees, polos"},
                    "Bottoms": {"count": "10-12", "details": "Performance shorts (5\", 7\", 9\"), training shorts"},
                    "Swim": {"count": "5-6", "details": "Board shorts, swim trunks"},
                    "Accessories": {"count": "3-4", "details": "Hats, sunglasses, bags"}
                },
                "colors": ["Royal Blue", "White", "Sunset Orange", "Navy", "Aqua"],
                "price_points": "$48-$128",
                "key_fabrics": "Ultra-lightweight, quick-dry, UV protection"
            },
            "womens": {
                "sku_count": "20-24",
                "categories": {
                    "Tops": {"count": "8-10", "details": "Performance tanks, breathable tees"},
                    "Bottoms": {"count": "8-10", "details": "Performance shorts, bike shorts, skorts"},
                    "Sports Bras": {"count": "3-4", "details": "Light & medium support bras"},
                    "Accessories": {"count": "1-2", "details": "Hats, bags"}
                },
                "colors": ["Royal Blue", "White", "Coral", "Aqua", "Tropical Print"],
                "price_points": "$48-$118",
                "key_fabrics": "Ultra-lightweight, quick-dry"
            }
        },
        "June": {
            "type": "Monthly Drop",
            "theme": "Summer Essentials / Travel Ready",
            "total_skus": "15-20",
            "color_strategy": "Navy, white, chambray, neutral travel-friendly palette",
            "mens": {
                "sku_count": "10-13",
                "categories": {
                    "Tops": {"count": "5-6", "details": "Packable polos, wrinkle-free tees"},
                    "Bottoms": {"count": "3-4", "details": "Quick-dry shorts, travel pants"},
                    "Accessories": {"count": "2-3", "details": "Travel bags, packing cubes, belts"}
                },
                "colors": ["Navy", "White", "Chambray", "Khaki"],
                "price_points": "$58-$108",
                "key_fabrics": "Wrinkle-resistant, quick-dry"
            },
            "womens": {
                "sku_count": "5-7",
                "categories": {
                    "Tops": {"count": "2-3", "details": "Packable tees, wrinkle-free tanks"},
                    "Bottoms": {"count": "2-3", "details": "Quick-dry leggings, travel joggers"},
                    "Accessories": {"count": "1", "details": "Travel bags"}
                },
                "colors": ["Navy", "White", "Chambray", "Black"],
                "price_points": "$48-$98",
                "key_fabrics": "Wrinkle-resistant, quick-dry"
            }
        },
        "July": {
            "type": "Monthly Drop",
            "theme": "Independence / Americana",
            "total_skus": "12-18",
            "color_strategy": "Red, navy, white combinations, patriotic prints",
            "mens": {
                "sku_count": "8-12",
                "categories": {
                    "Tops": {"count": "4-6", "details": "Americana tees, flag print tanks"},
                    "Bottoms": {"count": "3-4", "details": "Red/navy/white shorts"},
                    "Accessories": {"count": "1-2", "details": "American flag hats, bags"}
                },
                "colors": ["Navy", "White", "Red", "Americana Print"],
                "price_points": "$48-$88",
                "key_fabrics": "Cotton blends, performance fabrics"
            },
            "womens": {
                "sku_count": "4-6",
                "categories": {
                    "Tops": {"count": "2-3", "details": "Americana tanks, patriotic tees"},
                    "Bottoms": {"count": "1-2", "details": "Red/navy/white shorts or leggings"},
                    "Accessories": {"count": "1", "details": "Flag print accessories"}
                },
                "colors": ["Navy", "White", "Red"],
                "price_points": "$48-$78",
                "key_fabrics": "Cotton blends"
            }
        },
        "August": {
            "type": "FALL COLLECTION",
            "theme": "Back to Routine / Fall Layering",
            "total_skus": "75-90",
            "color_strategy": "Autumn palette: burgundy, forest, charcoal, rust, camel",
            "mens": {
                "sku_count": "45-54",
                "categories": {
                    "Outerwear": {"count": "15-18", "details": "Hoodies, quarter-zips, vests, jackets"},
                    "Tops": {"count": "15-18", "details": "Long-sleeve tees, henleys, pullovers"},
                    "Bottoms": {"count": "10-12", "details": "Performance joggers, training pants, chinos"},
                    "Accessories": {"count": "5-6", "details": "Beanies, scarves, gloves"}
                },
                "colors": ["Charcoal", "Burgundy", "Forest Green", "Rust", "Black", "Camel"],
                "price_points": "$58-$198",
                "key_fabrics": "Fleece, thermal, midweight performance"
            },
            "womens": {
                "sku_count": "30-36",
                "categories": {
                    "Outerwear": {"count": "10-12", "details": "Hoodies, jackets, vests"},
                    "Tops": {"count": "10-12", "details": "Long-sleeve tees, pullovers"},
                    "Bottoms": {"count": "7-9", "details": "Leggings, joggers, training pants"},
                    "Accessories": {"count": "3-4", "details": "Beanies, scarves"}
                },
                "colors": ["Charcoal", "Burgundy", "Rust", "Black", "Camel", "Forest Green"],
                "price_points": "$48-$178",
                "key_fabrics": "Fleece, thermal, midweight performance"
            }
        },
        "September": {
            "type": "Monthly Drop",
            "theme": "Fall Fitness / New Season Energy",
            "total_skus": "20-25",
            "color_strategy": "Rich jewel tones: emerald, sapphire, garnet, gold",
            "mens": {
                "sku_count": "13-16",
                "categories": {
                    "Outerwear": {"count": "5-6", "details": "Transition jackets, windbreakers"},
                    "Tops": {"count": "4-5", "details": "Training long-sleeves, performance henleys"},
                    "Bottoms": {"count": "4-5", "details": "Training joggers, performance pants"}
                },
                "colors": ["Sapphire", "Emerald", "Garnet", "Black"],
                "price_points": "$58-$138",
                "key_fabrics": "Midweight performance, moisture-wicking"
            },
            "womens": {
                "sku_count": "7-9",
                "categories": {
                    "Outerwear": {"count": "3-4", "details": "Transition jackets"},
                    "Tops": {"count": "2-3", "details": "Training long-sleeves"},
                    "Bottoms": {"count": "2-3", "details": "Leggings, training joggers"}
                },
                "colors": ["Sapphire", "Emerald", "Garnet", "Gold"],
                "price_points": "$48-$128",
                "key_fabrics": "Midweight performance"
            }
        },
        "October": {
            "type": "Monthly Drop",
            "theme": "Cozy Performance / Cold Weather Prep",
            "total_skus": "18-22",
            "color_strategy": "Deep neutrals: black, charcoal, coffee, espresso",
            "mens": {
                "sku_count": "12-14",
                "categories": {
                    "Outerwear": {"count": "5-6", "details": "Fleece hoodies, insulated vests"},
                    "Tops": {"count": "4-5", "details": "Thermal long-sleeves, base layers"},
                    "Accessories": {"count": "3", "details": "Winter gloves, thermal beanies, neck warmers"}
                },
                "colors": ["Black", "Charcoal", "Coffee", "Espresso"],
                "price_points": "$58-$148",
                "key_fabrics": "Fleece, thermal, insulated"
            },
            "womens": {
                "sku_count": "6-8",
                "categories": {
                    "Outerwear": {"count": "3-4", "details": "Fleece hoodies, vests"},
                    "Tops": {"count": "2-3", "details": "Thermal long-sleeves, base layers"},
                    "Accessories": {"count": "1-2", "details": "Beanies, gloves"}
                },
                "colors": ["Black", "Charcoal", "Coffee"],
                "price_points": "$48-$138",
                "key_fabrics": "Fleece, thermal"
            }
        },
        "November": {
            "type": "HOLIDAY COLLECTION",
            "theme": "Gift Season / Premium Performance",
            "total_skus": "50-65",
            "color_strategy": "Gift-worthy: metallics, deep reds, premium blacks, silver, gold accents",
            "mens": {
                "sku_count": "30-39",
                "categories": {
                    "Outerwear": {"count": "10-12", "details": "Premium hoodies, bomber jackets, gift-ready vests"},
                    "Tops": {"count": "10-12", "details": "Premium tees, party-ready polos, athleisure tops"},
                    "Gift Sets": {"count": "6-8", "details": "Packaged sets (hoodie + jogger, accessories packs)"},
                    "Accessories": {"count": "4-7", "details": "Premium bags, gift boxes, luxury socks"}
                },
                "colors": ["Black", "Charcoal", "Deep Red", "Silver", "Metallic Accents"],
                "price_points": "$68-$228",
                "key_fabrics": "Premium fleece, luxury performance fabrics"
            },
            "womens": {
                "sku_count": "20-26",
                "categories": {
                    "Outerwear": {"count": "7-9", "details": "Premium hoodies, bomber jackets"},
                    "Tops": {"count": "6-8", "details": "Premium tanks, party-ready tops"},
                    "Gift Sets": {"count": "4-5", "details": "Packaged sets (hoodie + legging, accessories)"},
                    "Accessories": {"count": "3-4", "details": "Premium bags, gift boxes"}
                },
                "colors": ["Black", "Deep Red", "Silver", "Gold Accents", "Rose Gold"],
                "price_points": "$58-$198",
                "key_fabrics": "Premium fleece, luxury fabrics"
            }
        },
        "December": {
            "type": "Monthly Drop",
            "theme": "Winter Wellness / Cold Weather Essentials",
            "total_skus": "15-20",
            "color_strategy": "Winter whites, icy blues, charcoal, silver",
            "mens": {
                "sku_count": "10-13",
                "categories": {
                    "Outerwear": {"count": "4-5", "details": "Insulated jackets, heavy fleece"},
                    "Tops": {"count": "3-4", "details": "Heavy base layers, thermal tops"},
                    "Bottoms": {"count": "2-3", "details": "Thermal leggings, insulated joggers"},
                    "Recovery": {"count": "1-2", "details": "Recovery hoodies, comfort joggers"}
                },
                "colors": ["Charcoal", "Icy Blue", "Winter White", "Black"],
                "price_points": "$68-$158",
                "key_fabrics": "Heavy thermal, insulated, recovery fabrics"
            },
            "womens": {
                "sku_count": "5-7",
                "categories": {
                    "Outerwear": {"count": "2-3", "details": "Insulated jackets, fleece"},
                    "Tops": {"count": "2-3", "details": "Base layers, thermal tops"},
                    "Bottoms": {"count": "1-2", "details": "Thermal leggings"}
                },
                "colors": ["Charcoal", "Icy Blue", "Winter White"],
                "price_points": "$58-$148",
                "key_fabrics": "Heavy thermal, insulated"
            }
        }
    }

    # Month selector
    selected_month = st.selectbox(
        "Select Month to View Detailed Plan",
        list(drops.keys()),
        index=0
    )

    drop = drops[selected_month]

    # Display selected month details
    st.markdown(f"### {selected_month}: {drop['theme']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        drop_type_color = "🎉" if "COLLECTION" in drop['type'] else "📦"
        st.metric("Drop Type", f"{drop_type_color} {drop['type']}")
    with col2:
        st.metric("Total SKUs", drop['total_skus'])
    with col3:
        mens_sku = drop['mens']['sku_count']
        womens_sku = drop['womens']['sku_count']
        st.metric("Men's / Women's Split", f"{mens_sku} / {womens_sku}")

    st.markdown(f"**Color Strategy:** {drop['color_strategy']}")

    st.divider()

    # Gender breakdown side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 👔 Men's Assortment ({drop['mens']['sku_count']} SKUs)")

        # Category breakdown
        st.markdown("**Category Breakdown:**")
        mens_categories = []
        for cat, info in drop['mens']['categories'].items():
            mens_categories.append({
                "Category": cat,
                "SKU Count": info['count'],
                "Details": info['details']
            })
        st.dataframe(pd.DataFrame(mens_categories), hide_index=True, use_container_width=True)

        # Colors
        st.markdown("**Colors:**")
        colors_html = ""
        for color in drop['mens']['colors']:
            hex_color = get_color_hex(color)
            colors_html += f'<span style="display:inline-block;padding:5px 10px;margin:2px;background-color:{hex_color};color:{"white" if color.lower() in ["black", "navy", "charcoal"] else "black"};border-radius:3px;font-size:12px;">{color}</span>'
        st.markdown(colors_html, unsafe_allow_html=True)

        # Price & fabrics
        st.markdown(f"**Price Range:** {drop['mens']['price_points']}")
        st.markdown(f"**Key Fabrics:** {drop['mens']['key_fabrics']}")

    with col2:
        st.markdown(f"### 👗 Women's Assortment ({drop['womens']['sku_count']} SKUs)")

        # Category breakdown
        st.markdown("**Category Breakdown:**")
        womens_categories = []
        for cat, info in drop['womens']['categories'].items():
            womens_categories.append({
                "Category": cat,
                "SKU Count": info['count'],
                "Details": info['details']
            })
        st.dataframe(pd.DataFrame(womens_categories), hide_index=True, use_container_width=True)

        # Colors
        st.markdown("**Colors:**")
        colors_html = ""
        for color in drop['womens']['colors']:
            hex_color = get_color_hex(color)
            colors_html += f'<span style="display:inline-block;padding:5px 10px;margin:2px;background-color:{hex_color};color:{"white" if color.lower() in ["black", "navy", "charcoal"] else "black"};border-radius:3px;font-size:12px;">{color}</span>'
        st.markdown(colors_html, unsafe_allow_html=True)

        # Price & fabrics
        st.markdown(f"**Price Range:** {drop['womens']['price_points']}")
        st.markdown(f"**Key Fabrics:** {drop['womens']['key_fabrics']}")

    st.divider()

    # Annual overview calendar
    st.markdown("## 📅 Full Year at a Glance")

    # Create calendar view
    calendar_data = []
    for month, drop_info in drops.items():
        calendar_data.append({
            "Month": month,
            "Type": drop_info['type'],
            "Theme": drop_info['theme'],
            "Total SKUs": drop_info['total_skus'],
            "Men's": drop_info['mens']['sku_count'],
            "Women's": drop_info['womens']['sku_count']
        })

    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(
        calendar_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Month": st.column_config.TextColumn("Month", width="small"),
            "Type": st.column_config.TextColumn("Drop Type", width="medium"),
            "Theme": st.column_config.TextColumn("Theme", width="large"),
            "Total SKUs": st.column_config.TextColumn("Total", width="small"),
            "Men's": st.column_config.TextColumn("Men's", width="small"),
            "Women's": st.column_config.TextColumn("Women's", width="small")
        },
        height=500
    )

    st.divider()

    # Key strategic recommendations
    st.markdown("## 💡 Key Drop Strategy Principles")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Timing & Cadence:**
        - Monthly drops: 1st week of month
        - Seasonal collections: 3rd week of month
        - 8-10 week lifecycle for monthly
        - 12-16 week lifecycle for seasonal
        - Basics: continuous replenishment
        """)

    with col2:
        st.markdown("""
        **Markdown Strategy:**
        - Monthly: 4 weeks full price → 30% off
        - Seasonal: 8 weeks full price → tiered discount
        - Target 65%+ full price sell-through
        - Final clearance: 60-70% off
        - Never exceed 40% inventory on sale
        """)

    with col3:
        st.markdown("""
        **Inventory Allocation:**
        - Men's: 60% of $ budget
        - Women's: 40% of $ budget
        - Outerwear: 35% of seasonal budget
        - Tops: 40% of monthly budget
        - Plan receipts 4-6 weeks pre-drop
        """)


def display_data_chat(df):
    """Display chat interface for asking questions about the data"""
    st.markdown('<div class="section-header">💬 Data Chat Assistant</div>', unsafe_allow_html=True)

    st.info("Ask questions about your Rhone product data. The assistant will only use information from your actual product database.")

    # Password protection
    if "chat_authenticated" not in st.session_state:
        st.session_state.chat_authenticated = False

    if not st.session_state.chat_authenticated:
        st.warning("🔒 This feature requires authentication to prevent unauthorized API usage.")
        password = st.text_input("Enter password to access Data Chat:", type="password", key="chat_password")

        if st.button("Submit", key="chat_password_submit"):
            if password == "R3dR0b0t":
                st.session_state.chat_authenticated = True
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
        return

    # Check for API key - try environment variable first, then Streamlit secrets
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            pass

    if not api_key:
        st.warning("⚠️ Please set your ANTHROPIC_API_KEY. For local: use .env file. For Streamlit Cloud: add to secrets.")
        return

    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your product data..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare data context for Claude - create aggregate summary instead of full dataset
        # This reduces token usage significantly while maintaining accuracy

        # Calculate statistics
        stats = {
            "total_products": len(df),
            "categories": df["category"].value_counts().to_dict() if "category" in df.columns else {},
            "gender_breakdown": df["gender"].value_counts().to_dict() if "gender" in df.columns else {},
        }

        # Price statistics
        if "price" in df.columns:
            stats["price_stats"] = {
                "average": float(df["price"].mean()),
                "min": float(df["price"].min()),
                "max": float(df["price"].max()),
                "by_category": df.groupby("category")["price"].mean().to_dict() if "category" in df.columns else {},
                "by_gender": df.groupby("gender")["price"].mean().to_dict() if "gender" in df.columns else {}
            }

        # Sale price statistics
        if "sale_price" in df.columns:
            on_sale = df[df["sale_price"].notna()]
            stats["sale_stats"] = {
                "products_on_sale": len(on_sale),
                "percent_on_sale": float(len(on_sale) / len(df) * 100),
                "avg_sale_price": float(on_sale["sale_price"].mean()) if len(on_sale) > 0 else 0
            }

        # Color statistics
        if "colors" in df.columns:
            colors_exploded = df.explode("colors")
            colors_exploded = colors_exploded[colors_exploded["colors"].notna()]
            if len(colors_exploded) > 0:
                stats["color_stats"] = {
                    "top_colors": colors_exploded["colors"].value_counts().head(20).to_dict(),
                    "unique_colors": int(colors_exploded["colors"].nunique())
                }

        # Create compact CSV representation for detailed queries
        # Only include first 50 products to stay within token limits
        sample_products = df.head(50).to_dict('records')

        # Create system prompt with aggregate data
        system_prompt = f"""You are a data analyst assistant for Rhone product data.
You have access to product statistics and a sample of products. Answer questions using ONLY this data.

AGGREGATE STATISTICS:
{json.dumps(stats, indent=2)}

SAMPLE PRODUCTS (first 50 of {len(df)}):
{json.dumps(sample_products, indent=2)}

When answering questions:
1. Use the aggregate statistics for overall trends and summaries
2. Use the sample products for specific examples (note: sample is limited to first 50 products)
3. If asked about specific products not in the sample, use aggregate stats to provide general answers
4. If the data doesn't contain the requested information, clearly state it's not available
5. Be concise but thorough in your analysis
"""

        # Generate response with Claude
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                client = Anthropic(api_key=api_key)

                # Stream the response
                full_response = ""
                with client.messages.stream(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # Add assistant response to chat history
                st.session_state.chat_messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error generating response: {e}")

    # Add a button to clear chat history
    if st.session_state.chat_messages:
        if st.button("Clear Chat History"):
            st.session_state.chat_messages = []
            st.rerun()


def display_vuori_analysis(df):
    """Display Vuori competitor analysis with detailed metrics"""
    st.markdown('<div class="section-header">🎽 Vuori Competitor Analysis</div>', unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("No Vuori data available")
        return

    # 1. Total Products Metrics
    col1, col2, col3 = st.columns(3)

    total_products = len(df)
    mens_products = len(df[df["gender"] == "Men"]) if "gender" in df.columns else 0
    womens_products = len(df[df["gender"] == "Women"]) if "gender" in df.columns else 0

    with col1:
        st.metric("Total Products", f"{total_products:,}")

    with col2:
        st.metric("Men's Products", f"{mens_products:,}")

    with col3:
        st.metric("Women's Products", f"{womens_products:,}")

    st.divider()

    # 2. & 3. Men's and Women's Products by Category Pie Charts
    st.markdown("### 📊 Products by Category")

    if "category" in df.columns and "gender" in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Men's Products by Category Pie Chart
            mens_df = df[df["gender"] == "Men"]
            if len(mens_df) > 0:
                mens_category_counts = mens_df["category"].value_counts().reset_index()
                mens_category_counts.columns = ["Category", "Count"]
                mens_category_counts["Percent"] = (mens_category_counts["Count"] / mens_category_counts["Count"].sum() * 100).round(1)
                mens_category_counts["Label"] = mens_category_counts.apply(
                    lambda row: f"{row['Category']}<br>{row['Count']} ({row['Percent']}%)", axis=1
                )

                fig_mens_cat = px.pie(
                    mens_category_counts,
                    values="Count",
                    names="Category",
                    title="Men's Products by Category",
                    hole=0.3
                )
                fig_mens_cat.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
                )
                fig_mens_cat.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_mens_cat, use_container_width=True)
            else:
                st.info("No men's products found")

        with col2:
            # Women's Products by Category Pie Chart
            womens_df = df[df["gender"] == "Women"]
            if len(womens_df) > 0:
                womens_category_counts = womens_df["category"].value_counts().reset_index()
                womens_category_counts.columns = ["Category", "Count"]
                womens_category_counts["Percent"] = (womens_category_counts["Count"] / womens_category_counts["Count"].sum() * 100).round(1)
                womens_category_counts["Label"] = womens_category_counts.apply(
                    lambda row: f"{row['Category']}<br>{row['Count']} ({row['Percent']}%)", axis=1
                )

                fig_womens_cat = px.pie(
                    womens_category_counts,
                    values="Count",
                    names="Category",
                    title="Women's Products by Category",
                    hole=0.3
                )
                fig_womens_cat.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
                )
                fig_womens_cat.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_womens_cat, use_container_width=True)
            else:
                st.info("No women's products found")

    st.divider()

    # 4. Average Pricing by Category
    st.markdown("### 💰 Average Pricing by Category")

    if "price" in df.columns and "category" in df.columns:
        avg_price_by_cat = df.groupby("category")["price"].mean().sort_values(ascending=True).reset_index()
        avg_price_by_cat.columns = ["Category", "Avg Price"]
        avg_price_by_cat["Avg Price"] = avg_price_by_cat["Avg Price"].round(2)

        fig_avg_price = px.bar(
            avg_price_by_cat,
            x="Avg Price",
            y="Category",
            orientation="h",
            title="Average Price by Category",
            text="Avg Price",
            color="Avg Price",
            color_continuous_scale="Greens"
        )
        fig_avg_price.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig_avg_price.update_layout(
            height=400,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Average Price ($)",
            yaxis_title="Category"
        )
        st.plotly_chart(fig_avg_price, use_container_width=True)

    st.divider()

    # 5. Top 20 Most Common Colors Bar Chart
    st.markdown("### 🎨 Color Analysis")

    if "colors" in df.columns:
        # Explode colors column
        colors_df = df.explode("colors")
        colors_df = colors_df[colors_df["colors"].notna()]

        if len(colors_df) > 0:
            # Top 20 colors overall
            color_counts = colors_df["colors"].value_counts().head(20).reset_index()
            color_counts.columns = ["Color", "Count"]

            fig_top_colors = px.bar(
                color_counts,
                x="Count",
                y="Color",
                orientation="h",
                title="Top 20 Most Common Colors",
                text="Count",
                color="Count",
                color_continuous_scale="Viridis"
            )
            fig_top_colors.update_traces(textposition='outside')
            fig_top_colors.update_layout(
                height=600,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="Number of Products",
                yaxis_title="Color"
            )
            st.plotly_chart(fig_top_colors, use_container_width=True)

            st.divider()

            # 6. & 7. Top 10 Colors in Men's and Women's Products
            st.markdown("### 🎨 Top Colors by Gender")

            if "gender" in colors_df.columns:
                col1, col2 = st.columns(2)

                with col1:
                    # Top 10 Colors in Men's Products
                    mens_colors_df = colors_df[colors_df["gender"] == "Men"]
                    if len(mens_colors_df) > 0:
                        mens_color_counts = mens_colors_df["colors"].value_counts().head(10).reset_index()
                        mens_color_counts.columns = ["Color", "Count"]

                        fig_mens_colors = px.bar(
                            mens_color_counts,
                            x="Count",
                            y="Color",
                            orientation="h",
                            title="Top 10 Colors in Men's Products",
                            text="Count",
                            color="Count",
                            color_continuous_scale="Blues"
                        )
                        fig_mens_colors.update_traces(textposition='outside')
                        fig_mens_colors.update_layout(
                            height=400,
                            showlegend=False,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Number of Products",
                            yaxis_title="Color"
                        )
                        st.plotly_chart(fig_mens_colors, use_container_width=True)
                    else:
                        st.info("No men's color data available")

                with col2:
                    # Top 10 Colors in Women's Products
                    womens_colors_df = colors_df[colors_df["gender"] == "Women"]
                    if len(womens_colors_df) > 0:
                        womens_color_counts = womens_colors_df["colors"].value_counts().head(10).reset_index()
                        womens_color_counts.columns = ["Color", "Count"]

                        fig_womens_colors = px.bar(
                            womens_color_counts,
                            x="Count",
                            y="Color",
                            orientation="h",
                            title="Top 10 Colors in Women's Products",
                            text="Count",
                            color="Count",
                            color_continuous_scale="Reds"
                        )
                        fig_womens_colors.update_traces(textposition='outside')
                        fig_womens_colors.update_layout(
                            height=400,
                            showlegend=False,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Number of Products",
                            yaxis_title="Color"
                        )
                        st.plotly_chart(fig_womens_colors, use_container_width=True)
                    else:
                        st.info("No women's color data available")
        else:
            st.warning("No color data available")
    else:
        st.warning("Color data not available in dataset")

    st.divider()

    # 8. & 9. Sale vs Full Price by Category
    st.markdown("### 🏷️ Sale vs Full Price by Category")

    if "on_sale" in df.columns and "category" in df.columns and "gender" in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Men's Products: Sale vs Full Price by Category
            mens_df = df[df["gender"] == "Men"]
            if len(mens_df) > 0:
                mens_sale_by_cat = mens_df.groupby(["category", "on_sale"]).size().reset_index(name="count")
                mens_sale_by_cat["Status"] = mens_sale_by_cat["on_sale"].apply(lambda x: "On Sale" if x else "Full Price")

                fig_mens_sale = px.bar(
                    mens_sale_by_cat,
                    x="count",
                    y="category",
                    color="Status",
                    orientation="h",
                    title="Men's Products: Sale vs Full Price by Category",
                    text="count",
                    barmode="stack",
                    color_discrete_map={"On Sale": "#EF553B", "Full Price": "#636EFA"}
                )
                fig_mens_sale.update_traces(textposition='inside')
                fig_mens_sale.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Products",
                    yaxis_title="Category"
                )
                st.plotly_chart(fig_mens_sale, use_container_width=True)
            else:
                st.info("No men's sale data available")

        with col2:
            # Women's Products: Sale vs Full Price by Category
            womens_df = df[df["gender"] == "Women"]
            if len(womens_df) > 0:
                womens_sale_by_cat = womens_df.groupby(["category", "on_sale"]).size().reset_index(name="count")
                womens_sale_by_cat["Status"] = womens_sale_by_cat["on_sale"].apply(lambda x: "On Sale" if x else "Full Price")

                fig_womens_sale = px.bar(
                    womens_sale_by_cat,
                    x="count",
                    y="category",
                    color="Status",
                    orientation="h",
                    title="Women's Products: Sale vs Full Price by Category",
                    text="count",
                    barmode="stack",
                    color_discrete_map={"On Sale": "#EF553B", "Full Price": "#636EFA"}
                )
                fig_womens_sale.update_traces(textposition='inside')
                fig_womens_sale.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Products",
                    yaxis_title="Category"
                )
                st.plotly_chart(fig_womens_sale, use_container_width=True)
            else:
                st.info("No women's sale data available")

    st.divider()

    # 10. Sale Statistics
    st.markdown("### 📊 Sale Statistics")

    if "on_sale" in df.columns and "price" in df.columns:
        col1, col2, col3 = st.columns(3)

        # Calculate metrics
        on_sale_count = df["on_sale"].sum()
        on_sale_pct = (on_sale_count / len(df)) * 100 if len(df) > 0 else 0

        avg_full_price = df["price"].mean() if "price" in df.columns else 0

        # Calculate average sale price (only from products that are on sale)
        sale_df = df[df["on_sale"] == True]
        if "sale_price" in df.columns and len(sale_df) > 0:
            avg_sale_price = sale_df["sale_price"].mean()
        else:
            avg_sale_price = 0

        with col1:
            st.metric("% of Products on Sale", f"{on_sale_pct:.1f}%")

        with col2:
            st.metric("Average Full Price", f"${avg_full_price:.2f}")

        with col3:
            st.metric("Average Sale Price", f"${avg_sale_price:.2f}" if avg_sale_price > 0 else "N/A")
    else:
        st.info("Sale and pricing data not available")


def main():
    """Main dashboard function"""

    # Header
    st.markdown('<div class="main-header">👕 Rhone Product Analytics Dashboard</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Select Analysis",
            [
                "Overview",
                "Category Analysis",
                "Color Analysis",
                "Sales & Pricing",
                "Line Plan",
                # "Drop Schedule",  # Hidden for now
                "Data Chat",
                "Raw Data",
                "--- Competitor Analysis ---",
                "Vuori Analysis"
            ]
        )

        st.divider()

        st.subheader("Data Info")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Load data based on selected page
    if page == "Vuori Analysis":
        # Load Vuori data for competitor analysis
        with st.spinner("Loading Vuori product data..."):
            df = load_data(brand_filter="Vuori")
        brand_name = "Vuori"
    else:
        # Load Rhone data for all other pages (filter out competitors)
        with st.spinner("Loading product data..."):
            df = load_data(brand_filter="Rhone")
        brand_name = "Rhone"

    if df is None:
        st.error("No data available. Please ensure you have scraped data and uploaded it to Supabase.")
        st.info("Steps to get started:\n1. Run the scraper: `cd scraper && scrapy crawl rhone`\n2. Upload data: `python database/upload_data.py`")
        return

    st.sidebar.success(f"Loaded {len(df)} {brand_name} products")
    if "scraped_at" in df.columns:
        latest_scrape = pd.to_datetime(df["scraped_at"]).max()
        if pd.notna(latest_scrape):
            st.sidebar.info(f"Last updated: {latest_scrape.strftime('%Y-%m-%d %H:%M')}")

    # Display selected page
    if page == "--- Competitor Analysis ---":
        st.info("Please select a competitor analysis page from the navigation menu.")
        return

    elif page == "Vuori Analysis":
        display_vuori_analysis(df)

    elif page == "Overview":
        display_overview(df)

    elif page == "Category Analysis":
        display_category_analysis(df)

    elif page == "Color Analysis":
        display_color_analysis(df)

    elif page == "Sales & Pricing":
        display_sales_analysis(df)

    elif page == "Line Plan":
        display_line_plan(df)

    elif page == "Drop Schedule":
        display_drop_schedule(df)

    elif page == "Data Chat":
        display_data_chat(df)

    elif page == "Raw Data":
        st.markdown('<div class="section-header">📄 Raw Data</div>', unsafe_allow_html=True)

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            if "category" in df.columns:
                categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
                selected_category = st.selectbox("Filter by Category", categories)
            else:
                selected_category = "All"

        with col2:
            if "gender" in df.columns:
                genders = ["All"] + sorted(df["gender"].dropna().unique().tolist())
                selected_gender = st.selectbox("Filter by Gender", genders)
            else:
                selected_gender = "All"

        with col3:
            if "is_best_seller" in df.columns:
                best_seller_filter = st.selectbox("Best Sellers Only", ["All", "Yes", "No"])
            else:
                best_seller_filter = "All"

        # Apply filters
        filtered_df = df.copy()

        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]

        if selected_gender != "All":
            filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

        if best_seller_filter == "Yes":
            filtered_df = filtered_df[filtered_df["is_best_seller"] == True]
        elif best_seller_filter == "No":
            filtered_df = filtered_df[filtered_df["is_best_seller"] == False]

        st.write(f"Showing {len(filtered_df)} products")

        # Display data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"rhone_products_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
