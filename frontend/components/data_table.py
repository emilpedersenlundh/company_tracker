"""Data table component for displaying records."""

import streamlit as st
import pandas as pd
from typing import Any


def render_data_table(
    data: list[dict[str, Any]],
    title: str | None = None,
    exclude_columns: list[str] | None = None,
    column_config: dict[str, Any] | None = None,
) -> pd.DataFrame | None:
    """
    Render a data table with optional configuration.

    Args:
        data: List of records to display
        title: Optional title for the table
        exclude_columns: Columns to exclude from display
        column_config: Streamlit column configuration

    Returns:
        DataFrame of the data, or None if no data
    """
    if not data:
        st.info("No data to display")
        return None

    if title:
        st.subheader(title)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Exclude columns
    if exclude_columns:
        df = df.drop(columns=[c for c in exclude_columns if c in df.columns], errors="ignore")

    # Display with configuration
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )

    return df


def render_selectable_table(
    data: list[dict[str, Any]],
    id_column: str,
    display_columns: list[str] | None = None,
) -> int | None:
    """
    Render a table where user can select a row.

    Args:
        data: List of records
        id_column: Column containing the unique ID
        display_columns: Columns to display

    Returns:
        Selected ID or None
    """
    if not data:
        st.info("No data to display")
        return None

    df = pd.DataFrame(data)

    if display_columns:
        display_df = df[display_columns]
    else:
        display_df = df

    # Create selection options
    options = {
        f"{row[id_column]}: {' | '.join(str(row[c]) for c in display_columns[:3] if c != id_column)}": row[id_column]
        for _, row in df.iterrows()
    }

    if not options:
        return None

    selected = st.selectbox("Select a record", options.keys())
    return options[selected] if selected else None
