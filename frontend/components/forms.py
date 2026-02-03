"""Form components for creating/updating records."""

import streamlit as st
from typing import Any
from decimal import Decimal


def render_company_form(existing: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """
    Render a form for creating/updating a company.

    Args:
        existing: Existing company data for editing

    Returns:
        Form data if submitted, None otherwise
    """
    with st.form("company_form"):
        st.subheader("Company" if not existing else "Edit Company")

        company_id = st.number_input(
            "Company ID",
            min_value=1,
            value=existing.get("company_id", 1) if existing else 1,
            disabled=existing is not None,
        )

        company_name = st.text_input(
            "Company Name",
            value=existing.get("company_name", "") if existing else "",
            max_chars=255,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            percentage_a = st.number_input(
                "Percentage A",
                min_value=0.0,
                max_value=1.0,
                value=float(existing.get("percentage_a") or 0) if existing else 0.0,
                step=0.01,
                format="%.4f",
            )
        with col2:
            percentage_b = st.number_input(
                "Percentage B",
                min_value=0.0,
                max_value=1.0,
                value=float(existing.get("percentage_b") or 0) if existing else 0.0,
                step=0.01,
                format="%.4f",
            )
        with col3:
            percentage_c = st.number_input(
                "Percentage C",
                min_value=0.0,
                max_value=1.0,
                value=float(existing.get("percentage_c") or 0) if existing else 0.0,
                step=0.01,
                format="%.4f",
            )

        submitted = st.form_submit_button("Save Company")

        if submitted:
            if not company_name:
                st.error("Company name is required")
                return None
            return {
                "company_id": int(company_id),
                "company_name": company_name,
                "percentage_a": percentage_a if percentage_a > 0 else None,
                "percentage_b": percentage_b if percentage_b > 0 else None,
                "percentage_c": percentage_c if percentage_c > 0 else None,
            }
    return None


def render_metric_form(
    existing: dict[str, Any] | None = None,
    companies: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """
    Render a form for creating/updating a metric.

    Args:
        existing: Existing metric data for editing
        companies: List of companies for dropdown

    Returns:
        Form data if submitted, None otherwise
    """
    with st.form("metric_form"):
        st.subheader("Metric" if not existing else "Edit Metric")

        # Company selection
        if companies:
            company_options = {c["company_name"]: c["company_id"] for c in companies}
            selected_company = st.selectbox(
                "Company",
                options=list(company_options.keys()),
                disabled=existing is not None,
            )
            company_id = company_options[selected_company]
        else:
            company_id = st.number_input(
                "Company ID",
                min_value=1,
                value=existing.get("company_id", 1) if existing else 1,
                disabled=existing is not None,
            )

        col1, col2 = st.columns(2)
        with col1:
            country_code = st.text_input(
                "Country Code",
                value=existing.get("country_code", "") if existing else "",
                max_chars=3,
                disabled=existing is not None,
            )
        with col2:
            year = st.number_input(
                "Year",
                min_value=1900,
                max_value=2100,
                value=existing.get("year", 2024) if existing else 2024,
                disabled=existing is not None,
            )

        revenue = st.number_input(
            "Revenue",
            min_value=0.0,
            value=float(existing.get("revenue") or 0) if existing else 0.0,
            step=1000.0,
            format="%.2f",
        )

        gross_profit = st.number_input(
            "Gross Profit",
            value=float(existing.get("gross_profit") or 0) if existing else 0.0,
            step=1000.0,
            format="%.2f",
        )

        headcount = st.number_input(
            "Headcount",
            min_value=0,
            value=existing.get("headcount") or 0 if existing else 0,
            step=1,
        )

        submitted = st.form_submit_button("Save Metric")

        if submitted:
            if not country_code:
                st.error("Country code is required")
                return None
            return {
                "company_id": int(company_id),
                "country_code": country_code.upper(),
                "year": int(year),
                "revenue": revenue if revenue > 0 else None,
                "gross_profit": gross_profit if gross_profit != 0 else None,
                "headcount": headcount if headcount > 0 else None,
            }
    return None


def render_product_form(existing: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """
    Render a form for creating/updating a product.

    Args:
        existing: Existing product data for editing

    Returns:
        Form data if submitted, None otherwise
    """
    with st.form("product_form"):
        st.subheader("Product" if not existing else "Edit Product")

        product_class_3_id = st.number_input(
            "Product Class 3 ID",
            min_value=1,
            value=existing.get("product_class_3_id", 1) if existing else 1,
            disabled=existing is not None,
        )

        class_level_1 = st.text_input(
            "Class Level 1",
            value=existing.get("class_level_1", "") if existing else "",
            max_chars=100,
        )

        class_level_2 = st.text_input(
            "Class Level 2",
            value=existing.get("class_level_2", "") if existing else "",
            max_chars=100,
        )

        class_level_3 = st.text_input(
            "Class Level 3",
            value=existing.get("class_level_3", "") if existing else "",
            max_chars=100,
        )

        submitted = st.form_submit_button("Save Product")

        if submitted:
            return {
                "product_class_3_id": int(product_class_3_id),
                "class_level_1": class_level_1 or None,
                "class_level_2": class_level_2 or None,
                "class_level_3": class_level_3 or None,
            }
    return None


def render_share_form(
    existing: dict[str, Any] | None = None,
    companies: list[dict[str, Any]] | None = None,
    products: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """
    Render a form for creating/updating a share.

    Args:
        existing: Existing share data for editing
        companies: List of companies for dropdown
        products: List of products for dropdown

    Returns:
        Form data if submitted, None otherwise
    """
    with st.form("share_form"):
        st.subheader("Market Share" if not existing else "Edit Market Share")

        # Company selection
        if companies:
            company_options = {c["company_name"]: c["company_id"] for c in companies}
            selected_company = st.selectbox(
                "Company",
                options=list(company_options.keys()),
                disabled=existing is not None,
            )
            company_id = company_options[selected_company]
        else:
            company_id = st.number_input(
                "Company ID",
                min_value=1,
                value=existing.get("company_id", 1) if existing else 1,
                disabled=existing is not None,
            )

        country_code = st.text_input(
            "Country Code",
            value=existing.get("country_code", "") if existing else "",
            max_chars=3,
            disabled=existing is not None,
        )

        # Product selection
        if products:
            product_options = {
                f"{p['product_class_3_id']}: {p.get('class_level_3', 'N/A')}": p["product_class_3_id"]
                for p in products
            }
            selected_product = st.selectbox(
                "Product",
                options=list(product_options.keys()),
                disabled=existing is not None,
            )
            product_class_3_id = product_options[selected_product]
        else:
            product_class_3_id = st.number_input(
                "Product Class 3 ID",
                min_value=1,
                value=existing.get("product_class_3_id", 1) if existing else 1,
                disabled=existing is not None,
            )

        share_percentage = st.number_input(
            "Share Percentage",
            min_value=0.0,
            max_value=1.0,
            value=float(existing.get("share_percentage") or 0) if existing else 0.0,
            step=0.01,
            format="%.4f",
        )

        submitted = st.form_submit_button("Save Share")

        if submitted:
            if not country_code:
                st.error("Country code is required")
                return None
            return {
                "company_id": int(company_id),
                "country_code": country_code.upper(),
                "product_class_3_id": int(product_class_3_id),
                "share_percentage": share_percentage if share_percentage > 0 else None,
            }
    return None
