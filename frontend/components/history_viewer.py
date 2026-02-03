"""History viewer component for displaying version history."""

import streamlit as st
import pandas as pd
from typing import Any


def render_history_viewer(
    history: list[dict[str, Any]],
    entity_name: str = "Record",
    exclude_columns: list[str] | None = None,
) -> None:
    """
    Display version history with timeline and details.

    Args:
        history: List of historical records (newest first)
        entity_name: Name of the entity for display
        exclude_columns: Columns to exclude from display
    """
    if not history:
        st.warning(f"No {entity_name.lower()} history found")
        return

    exclude = set(exclude_columns or [])

    st.subheader(f"Version History ({len(history)} versions)")

    # Create version labels
    versions = []
    for i, h in enumerate(history):
        status = "Current" if h.get("is_current") else "Superseded"
        valid_from = h.get("valid_from", "")[:19]
        versions.append(f"v{len(history) - i}: {valid_from} ({status})")

    # Version selector
    selected_idx = st.selectbox(
        "Select version to view",
        range(len(versions)),
        format_func=lambda x: versions[x],
    )

    record = history[selected_idx]

    # Status badges
    col1, col2, col3 = st.columns(3)
    with col1:
        if record.get("is_current"):
            st.success("Current Version")
        else:
            st.warning("Superseded")
    with col2:
        st.info(f"Created by: {record.get('created_by', 'system')}")
    with col3:
        st.info(f"Record ID: {record.get('record_id', 'N/A')}")

    # Temporal info
    col1, col2 = st.columns(2)
    with col1:
        st.text(f"Valid From: {record.get('valid_from', 'N/A')}")
    with col2:
        valid_to = record.get("valid_to")
        st.text(f"Valid To: {valid_to if valid_to else 'Present'}")

    # Record data
    st.markdown("**Record Data:**")
    display_data = {
        k: v for k, v in record.items()
        if k not in exclude and k not in ["valid_from", "valid_to", "is_current", "created_by", "record_id"]
    }
    df = pd.DataFrame([display_data])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Show diff with previous version if not the oldest
    if selected_idx < len(history) - 1:
        with st.expander("Show changes from previous version"):
            prev_record = history[selected_idx + 1]
            changes = []
            for key in display_data:
                old_val = prev_record.get(key)
                new_val = record.get(key)
                if old_val != new_val:
                    changes.append({
                        "Field": key,
                        "Previous": old_val,
                        "Current": new_val,
                    })
            if changes:
                st.dataframe(pd.DataFrame(changes), use_container_width=True, hide_index=True)
            else:
                st.info("No changes detected")
