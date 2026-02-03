"""Metrics management page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from frontend.api_client import get_client
from frontend.components.forms import render_metric_form

st.set_page_config(page_title="Metrics - Company Tracker", page_icon="📊", layout="wide")

API_URL = st.session_state.get("api_url", "http://localhost:8000")
client = get_client(API_URL)

st.title("📊 Metrics")

tab1, tab2, tab3 = st.tabs(["Browse", "Create/Edit", "Analytics"])

with tab1:
    st.subheader("Company Metrics")

    # Filters
    col1, col2, col3 = st.columns(3)

    try:
        companies = client.list_companies()
        company_map = {c["company_name"]: c["company_id"] for c in companies}
        company_map["All Companies"] = None

        with col1:
            selected_company = st.selectbox("Company", options=list(company_map.keys()))
            company_id = company_map[selected_company]

        with col2:
            country_code = st.text_input("Country Code", placeholder="e.g., DK, US")

        with col3:
            year = st.number_input("Year", min_value=0, max_value=2100, value=0)
            year_filter = year if year > 0 else None

        # Fetch metrics
        metrics = client.list_metrics(
            company_id=company_id,
            country_code=country_code if country_code else None,
            year=year_filter,
        )

        if metrics:
            df = pd.DataFrame(metrics)

            # Format currency columns
            for col in ["revenue", "gross_profit"]:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: f"${float(x):,.2f}" if x else "-"
                    )

            # Format headcount
            if "headcount" in df.columns:
                df["headcount"] = df["headcount"].apply(
                    lambda x: f"{int(x):,}" if x else "-"
                )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "company_id": st.column_config.NumberColumn("Company ID"),
                    "country_code": st.column_config.TextColumn("Country"),
                    "year": st.column_config.NumberColumn("Year"),
                    "revenue": st.column_config.TextColumn("Revenue"),
                    "gross_profit": st.column_config.TextColumn("Gross Profit"),
                    "headcount": st.column_config.TextColumn("Headcount"),
                },
            )

            # Export
            csv = pd.DataFrame(metrics).to_csv(index=False)
            st.download_button("Download CSV", csv, "metrics.csv", "text/csv")
        else:
            st.info("No metrics found")

    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    st.subheader("Create or Update Metric")

    try:
        companies = client.list_companies()
        form_data = render_metric_form(companies=companies)

        if form_data:
            result = client.upsert_metric(form_data)
            if result.get("is_new"):
                st.success(f"Metric saved! Record ID: {result['record_id']}")
            else:
                st.info(f"No changes detected. Record ID: {result['record_id']}")
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

with tab3:
    st.subheader("Metrics Analytics")

    try:
        metrics = client.list_metrics(limit=1000)

        if metrics:
            df = pd.DataFrame(metrics)

            # Convert to numeric
            df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
            df["gross_profit"] = pd.to_numeric(df["gross_profit"], errors="coerce")
            df["headcount"] = pd.to_numeric(df["headcount"], errors="coerce")

            # Revenue by company
            if "revenue" in df.columns and df["revenue"].notna().any():
                st.subheader("Revenue by Company")
                revenue_by_company = df.groupby("company_id")["revenue"].sum().reset_index()
                fig = px.bar(
                    revenue_by_company,
                    x="company_id",
                    y="revenue",
                    title="Total Revenue by Company",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Revenue trend by year
            if "year" in df.columns:
                st.subheader("Revenue Trend by Year")
                revenue_by_year = df.groupby("year")["revenue"].sum().reset_index()
                fig = px.line(
                    revenue_by_year,
                    x="year",
                    y="revenue",
                    title="Revenue Trend",
                    markers=True,
                )
                st.plotly_chart(fig, use_container_width=True)

            # Headcount by country
            if "headcount" in df.columns and df["headcount"].notna().any():
                st.subheader("Headcount by Country")
                headcount_by_country = df.groupby("country_code")["headcount"].sum().reset_index()
                fig = px.pie(
                    headcount_by_country,
                    values="headcount",
                    names="country_code",
                    title="Headcount Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No metrics data available for analytics")

    except Exception as e:
        st.error(f"Error loading analytics: {e}")
