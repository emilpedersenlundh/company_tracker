"""Companies management page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime

from frontend.api_client import get_client
from frontend.components.history_viewer import render_history_viewer
from frontend.components.forms import render_company_form

st.set_page_config(page_title="Companies - Company Tracker", page_icon="🏢", layout="wide")

# Get client from session or create new
API_URL = st.session_state.get("api_url", "http://localhost:8000")
client = get_client(API_URL)

st.title("🏢 Companies")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Browse", "Create/Edit", "History"])

with tab1:
    st.subheader("Current Companies")

    # Search filter
    search = st.text_input("Search by name", placeholder="Enter company name...")

    # Fetch and display companies
    try:
        companies = client.list_companies(name=search if search else None)

        if companies:
            df = pd.DataFrame(companies)

            # Format percentages
            for col in ["percentage_a", "percentage_b", "percentage_c"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: f"{float(x):.2%}" if x else "-")

            # Format date
            if "valid_from" in df.columns:
                df["valid_from"] = df["valid_from"].apply(lambda x: x[:19] if x else "-")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "company_id": st.column_config.NumberColumn("ID", width="small"),
                    "company_name": st.column_config.TextColumn("Company Name", width="large"),
                    "percentage_a": st.column_config.TextColumn("% A"),
                    "percentage_b": st.column_config.TextColumn("% B"),
                    "percentage_c": st.column_config.TextColumn("% C"),
                    "valid_from": st.column_config.TextColumn("Last Updated"),
                },
            )

            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "companies.csv",
                "text/csv",
                key="download-companies",
            )
        else:
            st.info("No companies found")

    except Exception as e:
        st.error(f"Error loading companies: {e}")

with tab2:
    st.subheader("Create or Update Company")

    # Option to load existing company
    col1, col2 = st.columns([1, 3])
    with col1:
        load_id = st.number_input("Load Company ID", min_value=0, value=0, step=1)
    with col2:
        if load_id > 0:
            existing = client.get_company(load_id)
            if existing:
                st.success(f"Loaded: {existing['company_name']}")
            else:
                st.warning(f"Company {load_id} not found - will create new")
                existing = None
        else:
            existing = None

    # Render form
    form_data = render_company_form(existing=existing)

    if form_data:
        try:
            result = client.upsert_company(form_data)
            if result.get("is_new"):
                st.success(f"Company saved! Record ID: {result['record_id']}")
            else:
                st.info(f"No changes detected. Existing record ID: {result['record_id']}")
            st.rerun()
        except Exception as e:
            st.error(f"Error saving company: {e}")

with tab3:
    st.subheader("Company History")

    # Company selector
    try:
        all_companies = client.list_companies()
        if all_companies:
            company_options = {f"{c['company_id']}: {c['company_name']}": c["company_id"] for c in all_companies}
            selected = st.selectbox("Select Company", options=list(company_options.keys()))

            if selected:
                company_id = company_options[selected]

                # Fetch history
                history = client.get_company_history(company_id)
                render_history_viewer(history, entity_name="Company")

                # Point-in-time query
                st.subheader("Point-in-Time Query")
                query_date = st.date_input("Select date")
                query_time = st.time_input("Select time")

                if st.button("Query"):
                    point_in_time = datetime.combine(query_date, query_time)
                    result = client.get_company_at_time(company_id, point_in_time)
                    if result:
                        st.success(f"Company state at {point_in_time}:")
                        st.json(result)
                    else:
                        st.warning(f"No record found at {point_in_time}")
        else:
            st.info("No companies available")

    except Exception as e:
        st.error(f"Error: {e}")
