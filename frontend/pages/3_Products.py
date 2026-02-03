"""Products management page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd

from frontend.api_client import get_client
from frontend.components.history_viewer import render_history_viewer
from frontend.components.forms import render_product_form

st.set_page_config(page_title="Products - Company Tracker", page_icon="📦", layout="wide")

API_URL = st.session_state.get("api_url", "http://localhost:8000")
client = get_client(API_URL)

st.title("📦 Products")

tab1, tab2, tab3 = st.tabs(["Browse", "Create/Edit", "History"])

with tab1:
    st.subheader("Product Hierarchy")

    # Filters
    col1, col2, col3 = st.columns(3)

    try:
        # Get unique values for filters
        all_products = client.list_products(limit=1000)

        level_1_options = ["All"] + list(set(p.get("class_level_1") or "" for p in all_products if p.get("class_level_1")))
        level_2_options = ["All"] + list(set(p.get("class_level_2") or "" for p in all_products if p.get("class_level_2")))

        with col1:
            level_1 = st.selectbox("Class Level 1", options=level_1_options)
        with col2:
            level_2 = st.selectbox("Class Level 2", options=level_2_options)
        with col3:
            name_search = st.text_input("Search Level 3", placeholder="Search...")

        # Fetch with filters
        products = client.list_products(
            class_level_1=level_1 if level_1 != "All" else None,
            class_level_2=level_2 if level_2 != "All" else None,
            name=name_search if name_search else None,
        )

        if products:
            df = pd.DataFrame(products)

            # Rename columns for display
            df = df.rename(columns={
                "product_class_3_id": "ID",
                "class_level_1": "Level 1",
                "class_level_2": "Level 2",
                "class_level_3": "Level 3",
                "valid_from": "Last Updated",
            })

            if "Last Updated" in df.columns:
                df["Last Updated"] = df["Last Updated"].apply(lambda x: x[:19] if x else "-")

            st.dataframe(df, use_container_width=True, hide_index=True)

            # Hierarchy tree view
            st.subheader("Hierarchy Tree")
            hierarchy = {}
            for p in products:
                l1 = p.get("class_level_1") or "Uncategorized"
                l2 = p.get("class_level_2") or "Uncategorized"
                l3 = p.get("class_level_3") or f"Product {p['product_class_3_id']}"

                if l1 not in hierarchy:
                    hierarchy[l1] = {}
                if l2 not in hierarchy[l1]:
                    hierarchy[l1][l2] = []
                hierarchy[l1][l2].append(l3)

            for l1, l2_dict in hierarchy.items():
                with st.expander(f"📁 {l1}"):
                    for l2, l3_list in l2_dict.items():
                        st.markdown(f"**📂 {l2}**")
                        for l3 in l3_list:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📄 {l3}")

            # Export
            csv = pd.DataFrame(products).to_csv(index=False)
            st.download_button("Download CSV", csv, "products.csv", "text/csv")
        else:
            st.info("No products found")

    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    st.subheader("Create or Update Product")

    # Load existing product
    col1, col2 = st.columns([1, 3])
    with col1:
        load_id = st.number_input("Load Product ID", min_value=0, value=0, step=1)
    with col2:
        if load_id > 0:
            existing = client.get_product(load_id)
            if existing:
                st.success(f"Loaded: {existing.get('class_level_3', 'Product')} (ID: {load_id})")
            else:
                st.warning(f"Product {load_id} not found - will create new")
                existing = None
        else:
            existing = None

    form_data = render_product_form(existing=existing)

    if form_data:
        try:
            result = client.upsert_product(form_data)
            if result.get("is_new"):
                st.success(f"Product saved! Record ID: {result['record_id']}")
            else:
                st.info(f"No changes detected. Record ID: {result['record_id']}")
            st.rerun()
        except Exception as e:
            st.error(f"Error saving product: {e}")

with tab3:
    st.subheader("Product History")

    try:
        products = client.list_products()
        if products:
            product_options = {
                f"{p['product_class_3_id']}: {p.get('class_level_3', 'N/A')}": p["product_class_3_id"]
                for p in products
            }
            selected = st.selectbox("Select Product", options=list(product_options.keys()))

            if selected:
                product_id = product_options[selected]
                history = client.get_product_history(product_id)
                render_history_viewer(history, entity_name="Product")
        else:
            st.info("No products available")

    except Exception as e:
        st.error(f"Error: {e}")
