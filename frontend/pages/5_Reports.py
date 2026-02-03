"""Reports and analytics page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from frontend.api_client import get_client

st.set_page_config(page_title="Reports - Company Tracker", page_icon="📑", layout="wide")

API_URL = st.session_state.get("api_url", "http://localhost:8000")
client = get_client(API_URL)

st.title("📑 Reports & Analytics")

tab1, tab2, tab3 = st.tabs(["Market Share Report", "Data Export", "System Stats"])

with tab1:
    st.subheader("Aggregated Market Share Report")

    col1, col2 = st.columns(2)

    try:
        products = client.list_products()

        with col1:
            country_filter = st.text_input("Filter by Country Code", placeholder="e.g., DK")

        with col2:
            product_options = {"All Products": None}
            product_options.update({
                f"{p['product_class_3_id']}: {p.get('class_level_3', 'N/A')}": p["product_class_3_id"]
                for p in products
            })
            selected_product = st.selectbox("Filter by Product", options=list(product_options.keys()))
            product_id = product_options[selected_product]

        # Fetch report
        report = client.get_market_share_report(
            country_code=country_filter if country_filter else None,
            product_class_3_id=product_id,
        )

        if report:
            # Get company names
            companies = client.list_companies()
            company_lookup = {c["company_id"]: c["company_name"] for c in companies}

            df = pd.DataFrame(report)
            df["company_name"] = df["company_id"].map(company_lookup)

            # Reorder columns
            df = df[["company_id", "company_name", "country_code", "total_share", "product_count"]]

            # Format
            df["total_share"] = df["total_share"].apply(lambda x: f"{x:.2%}")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "company_id": st.column_config.NumberColumn("Company ID"),
                    "company_name": st.column_config.TextColumn("Company Name"),
                    "country_code": st.column_config.TextColumn("Country"),
                    "total_share": st.column_config.TextColumn("Total Share"),
                    "product_count": st.column_config.NumberColumn("Products"),
                },
            )

            # Visualization
            raw_df = pd.DataFrame(report)
            raw_df["company_name"] = raw_df["company_id"].map(company_lookup)

            fig = px.bar(
                raw_df,
                x="company_name",
                y="total_share",
                color="country_code",
                title="Total Market Share by Company",
                labels={"total_share": "Total Share", "company_name": "Company"},
            )
            fig.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Companies", len(raw_df["company_id"].unique()))
            with col2:
                st.metric("Total Countries", len(raw_df["country_code"].unique()))
            with col3:
                st.metric("Avg Products/Company", f"{raw_df['product_count'].mean():.1f}")

        else:
            st.info("No data available for the selected filters")

    except Exception as e:
        st.error(f"Error loading report: {e}")

with tab2:
    st.subheader("Data Export")

    st.markdown("Export all current data from the system.")

    col1, col2 = st.columns(2)

    try:
        with col1:
            st.markdown("**Companies**")
            companies = client.list_companies(limit=1000)
            if companies:
                df = pd.DataFrame(companies)
                csv = df.to_csv(index=False)
                st.download_button(
                    f"Download Companies ({len(companies)} records)",
                    csv,
                    f"companies_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )
            else:
                st.info("No companies to export")

            st.markdown("**Products**")
            products = client.list_products(limit=1000)
            if products:
                df = pd.DataFrame(products)
                csv = df.to_csv(index=False)
                st.download_button(
                    f"Download Products ({len(products)} records)",
                    csv,
                    f"products_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )
            else:
                st.info("No products to export")

        with col2:
            st.markdown("**Metrics**")
            metrics = client.list_metrics(limit=1000)
            if metrics:
                df = pd.DataFrame(metrics)
                csv = df.to_csv(index=False)
                st.download_button(
                    f"Download Metrics ({len(metrics)} records)",
                    csv,
                    f"metrics_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )
            else:
                st.info("No metrics to export")

            st.markdown("**Shares**")
            shares = client.list_shares(limit=1000)
            if shares:
                df = pd.DataFrame(shares)
                csv = df.to_csv(index=False)
                st.download_button(
                    f"Download Shares ({len(shares)} records)",
                    csv,
                    f"shares_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )
            else:
                st.info("No shares to export")

    except Exception as e:
        st.error(f"Error preparing exports: {e}")

with tab3:
    st.subheader("System Statistics")

    try:
        # Collect stats
        companies = client.list_companies(limit=1000)
        metrics = client.list_metrics(limit=1000)
        products = client.list_products(limit=1000)
        shares = client.list_shares(limit=1000)

        # Summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Companies", len(companies))
        with col2:
            st.metric("Metrics", len(metrics))
        with col3:
            st.metric("Products", len(products))
        with col4:
            st.metric("Shares", len(shares))

        # Data distribution
        st.subheader("Data Distribution")

        col1, col2 = st.columns(2)

        with col1:
            if metrics:
                df = pd.DataFrame(metrics)
                if "country_code" in df.columns:
                    country_counts = df["country_code"].value_counts().reset_index()
                    country_counts.columns = ["Country", "Metrics Count"]
                    fig = px.pie(
                        country_counts,
                        values="Metrics Count",
                        names="Country",
                        title="Metrics by Country",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            if products:
                df = pd.DataFrame(products)
                if "class_level_1" in df.columns:
                    level_counts = df["class_level_1"].value_counts().reset_index()
                    level_counts.columns = ["Category", "Product Count"]
                    fig = px.bar(
                        level_counts,
                        x="Category",
                        y="Product Count",
                        title="Products by Category",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # API Health
        st.subheader("API Status")
        if client.health_check():
            st.success("API is healthy and responding")
        else:
            st.error("API is not responding")

    except Exception as e:
        st.error(f"Error loading statistics: {e}")
