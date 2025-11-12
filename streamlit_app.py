import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import sys
from pathlib import Path

# Add database module to path
sys.path.append(str(Path(__file__).parent / "database"))

from database.supabase_client import SupabaseClient

# Page configuration
st.set_page_config(
    page_title="Rhone Product Analytics Dashboard",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Load product data from Supabase"""
    try:
        client = SupabaseClient()
        products = client.get_all_products()

        if not products:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(products)

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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Products", len(df))

    with col2:
        categories = df["category"].nunique() if "category" in df.columns else 0
        st.metric("Categories", categories)

    with col3:
        best_sellers = df["is_best_seller"].sum() if "is_best_seller" in df.columns else 0
        st.metric("Best Sellers", int(best_sellers))

    with col4:
        homepage_products = df["is_homepage_product"].sum() if "is_homepage_product" in df.columns else 0
        st.metric("Homepage Products", int(homepage_products))


def display_category_analysis(df):
    """Display category analysis"""
    st.markdown('<div class="section-header">📦 Products per Category</div>', unsafe_allow_html=True)

    if "category" not in df.columns:
        st.warning("Category data not available")
        return

    # Products per category
    category_counts = df["category"].value_counts().reset_index()
    category_counts.columns = ["Category", "Count"]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title="Products by Category",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            category_counts,
            hide_index=True,
            use_container_width=True
        )

    # Products per category by gender
    if "gender" in df.columns:
        st.subheader("Products by Category and Gender")

        gender_category = df.groupby(["category", "gender"]).size().reset_index(name="count")

        fig = px.bar(
            gender_category,
            x="category",
            y="count",
            color="gender",
            title="Products by Category and Gender",
            barmode="group"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


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

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = px.bar(
            color_counts,
            x="Color",
            y="Count",
            title="Top 20 Most Common Colors",
            color="Count",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            color_counts,
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

        fig = px.bar(
            top_colors_per_category,
            x="category",
            y="count",
            color="colors",
            title="Top 5 Colors per Category",
            barmode="stack"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


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
    if "on_sale" in df.columns:
        on_sale_df = df[df["on_sale"] == True]
    else:
        on_sale_df = df[df["sale_price"].notna()]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Products on Sale", len(on_sale_df))

    with col2:
        sale_percentage = (len(on_sale_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("% on Sale", f"{sale_percentage:.1f}%")

    with col3:
        if "price" in df.columns:
            avg_price = df["price"].mean()
            st.metric("Avg Regular Price", f"${avg_price:.2f}")

    with col4:
        if "sale_price" in on_sale_df.columns and len(on_sale_df) > 0:
            avg_sale = on_sale_df["sale_price"].mean()
            st.metric("Avg Sale Price", f"${avg_sale:.2f}")

    # Calculate discount percentages
    if "price" in on_sale_df.columns and "sale_price" in on_sale_df.columns:
        discount_df = on_sale_df[on_sale_df["price"].notna() & on_sale_df["sale_price"].notna()].copy()

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

    # Sales by category
    if "category" in df.columns:
        st.subheader("Sales by Category")

        category_sales = df.groupby("category").agg({
            "on_sale": "sum" if "on_sale" in df.columns else "count"
        }).reset_index()
        category_sales.columns = ["Category", "Products on Sale"]

        fig = px.bar(
            category_sales,
            x="Category",
            y="Products on Sale",
            title="Sale Products by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

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
                "Fabric Analysis",
                "Sales & Pricing",
                "Best Sellers",
                "Homepage Products",
                "Raw Data"
            ]
        )

        st.divider()

        st.subheader("Data Info")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # Load data
    with st.spinner("Loading product data..."):
        df = load_data()

    if df is None:
        st.error("No data available. Please ensure you have scraped data and uploaded it to Supabase.")
        st.info("Steps to get started:\n1. Run the scraper: `cd scraper && scrapy crawl rhone`\n2. Upload data: `python database/upload_data.py`")
        return

    st.sidebar.success(f"Loaded {len(df)} products")
    if "scraped_at" in df.columns:
        latest_scrape = pd.to_datetime(df["scraped_at"]).max()
        st.sidebar.info(f"Last updated: {latest_scrape.strftime('%Y-%m-%d %H:%M')}")

    # Display selected page
    if page == "Overview":
        display_overview(df)
        st.divider()
        display_category_analysis(df)

    elif page == "Category Analysis":
        display_category_analysis(df)

    elif page == "Color Analysis":
        display_color_analysis(df)

    elif page == "Fabric Analysis":
        display_fabric_analysis(df)

    elif page == "Sales & Pricing":
        display_sales_analysis(df)

    elif page == "Best Sellers":
        display_best_sellers(df)

    elif page == "Homepage Products":
        display_homepage_analysis(df)

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
