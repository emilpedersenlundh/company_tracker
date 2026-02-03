"""Shares management page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px

from frontend.api_client import get_client
from frontend.components.forms import render_share_form

st.set_page_config(page_title="Shares - Company Tracker", page_icon="📈", layout="wide")

API_URL = st.session_state.get("api_url", "http://localhost:8000")
client = get_client(API_URL)

st.title("📈 Market Shares")

tab1, tab2, tab3 = st.tabs(["Browse", "Create/Edit", "Visualize"])

with tab1:
    st.subheader("Current Market Shares")

    # Filters
    col1, col2, col3 = st.columns(3)

    try:
        companies = client.list_companies()
        products = client.list_products()

        company_map = {"All Companies": None}
        company_map.update({c["company_name"]: c["company_id"] for c in companies})

        product_map = {"All Products": None}
        product_map.update({
            f"{p['product_class_3_id']}: {p.get('class_level_3', 'N/A')}": p["product_class_3_id"]
            for p in products
        })

        with col1:
            selected_company = st.selectbox("Company", options=list(company_map.keys()))
            company_id = company_map[selected_company]

        with col2:
            country_code = st.text_input("Country Code", placeholder="e.g., DK")

        with col3:
            selected_product = st.selectbox("Product", options=list(product_map.keys()))
            product_id = product_map[selected_product]

        # Fetch shares
        shares = client.list_shares(
            company_id=company_id,
            country_code=country_code if country_code else None,
            product_class_3_id=product_id,
        )

        if shares:
            df = pd.DataFrame(shares)

            # Format share percentage
            if "share_percentage" in df.columns:
                df["share_percentage"] = df["share_percentage"].apply(
                    lambda x: f"{float(x):.2%}" if x else "-"
                )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "company_id": st.column_config.NumberColumn("Company ID"),
                    "country_code": st.column_config.TextColumn("Country"),
                    "product_class_3_id": st.column_config.NumberColumn("Product ID"),
                    "share_percentage": st.column_config.TextColumn("Market Share"),
                },
            )

            # Export
            csv = pd.DataFrame(shares).to_csv(index=False)
            st.download_button("Download CSV", csv, "shares.csv", "text/csv")
        else:
            st.info("No shares found")

    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    st.subheader("Create or Update Market Share")

    try:
        companies = client.list_companies()
        products = client.list_products()

        form_data = render_share_form(companies=companies, products=products)

        if form_data:
            result = client.upsert_share(form_data)
            if result.get("is_new"):
                st.success(f"Share saved! Record ID: {result['record_id']}")
            else:
                st.info(f"No changes detected. Record ID: {result['record_id']}")
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

with tab3:
    st.subheader("Market Share Visualization")

    try:
        shares = client.list_shares(limit=1000)
        companies = client.list_companies()

        if shares and companies:
            df = pd.DataFrame(shares)
            company_lookup = {c["company_id"]: c["company_name"] for c in companies}
            df["company_name"] = df["company_id"].map(company_lookup)
            df["share_percentage"] = pd.to_numeric(df["share_percentage"], errors="coerce")

            # Country filter for visualization
            countries = df["country_code"].unique().tolist()
            selected_country = st.selectbox("Select Country", options=["All"] + countries)

            if selected_country != "All":
                df = df[df["country_code"] == selected_country]

            # Market share by company (pie chart)
            st.subheader("Market Share by Company")
            share_by_company = df.groupby("company_name")["share_percentage"].sum().reset_index()
            fig = px.pie(
                share_by_company,
                values="share_percentage",
                names="company_name",
                title=f"Market Share Distribution{' - ' + selected_country if selected_country != 'All' else ''}",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Market share by country (bar chart)
            if selected_country == "All":
                st.subheader("Market Share by Country")
                share_by_country = df.groupby("country_code")["share_percentage"].sum().reset_index()
                fig = px.bar(
                    share_by_country,
                    x="country_code",
                    y="share_percentage",
                    title="Total Market Share by Country",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Company comparison
            st.subheader("Company Comparison")
            fig = px.bar(
                df,
                x="company_name",
                y="share_percentage",
                color="country_code",
                barmode="group",
                title="Market Share Comparison",
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No share data available for visualization")

    except Exception as e:
        st.error(f"Error: {e}")
