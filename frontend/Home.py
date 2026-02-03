"""Main Streamlit application for Company Tracker."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import streamlit as st
from frontend.api_client import get_client

# Page configuration
st.set_page_config(
    page_title="Company Tracker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get default API URL from environment (for Docker) or use localhost
DEFAULT_API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Initialize API client
API_URL = st.sidebar.text_input(
    "API URL",
    value=DEFAULT_API_URL,
    help="URL of the Company Tracker API",
)

# Store in session state for other pages
st.session_state["api_url"] = API_URL

client = get_client(API_URL)

# User identification
user = st.sidebar.text_input(
    "Your Username",
    value="streamlit-user",
    help="Used for audit tracking (created_by field)",
)
client.set_user(user)

# Check API health
api_healthy = client.health_check()
if api_healthy:
    st.sidebar.success("API Connected")
else:
    st.sidebar.error("API Unavailable")

# Main page content
st.title("🏢 Company Tracker")

st.markdown("""
Welcome to the **Company Tracker** - a temporal data management system for tracking
companies, metrics, products, and market shares.

### Features

- **Append-Only Pattern**: All changes are tracked with full history
- **Point-in-Time Queries**: Query data as it was at any moment
- **Audit Trail**: All changes include user tracking
- **No Deletion**: Data is never deleted, only superseded

### Quick Navigation

Use the sidebar to navigate between pages:
- **Companies**: Manage company records
- **Metrics**: Track financial metrics by country/year
- **Products**: Product hierarchy management
- **Shares**: Market share tracking
- **Reports**: Analytics and reports
""")

# Dashboard stats
if api_healthy:
    st.header("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    try:
        companies = client.list_companies(limit=1000)
        metrics = client.list_metrics(limit=1000)
        products = client.list_products(limit=1000)
        shares = client.list_shares(limit=1000)

        with col1:
            st.metric("Companies", len(companies))
        with col2:
            st.metric("Metrics", len(metrics))
        with col3:
            st.metric("Products", len(products))
        with col4:
            st.metric("Shares", len(shares))

        # Recent activity
        if companies:
            st.subheader("Recent Companies")
            recent = sorted(companies, key=lambda x: x.get("valid_from", ""), reverse=True)[:5]
            for c in recent:
                st.text(f"• {c['company_name']} (ID: {c['company_id']}) - {c.get('valid_from', '')[:19]}")

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
else:
    st.warning("Connect to the API to view dashboard statistics.")
    st.info("""
    ### Getting Started

    1. Start the API server:
       ```bash
       source venv/bin/activate
       docker-compose up -d db
       alembic upgrade head
       uvicorn app.main:app --reload
       ```

    2. The API should be available at http://localhost:8000

    3. Refresh this page once the API is running
    """)
