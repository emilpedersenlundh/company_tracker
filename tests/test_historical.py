"""Tests for historical and point-in-time queries."""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_point_in_time_query_company(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test point-in-time query for company returns correct version."""
    # Create initial record
    response1 = await client.post("/api/companies", json=sample_company)
    assert response1.status_code == 200

    # Wait to ensure timestamps differ (SQLite has limited precision)
    await asyncio.sleep(1.1)

    # Update company
    updated = sample_company.copy()
    updated["company_name"] = "Novo Nordisk A/S"
    response2 = await client.post("/api/companies", json=updated)
    assert response2.status_code == 200

    # Get history to find exact timestamps
    history_response = await client.get(
        f"/api/companies/{sample_company['company_id']}/history"
    )
    history = history_response.json()
    # history[0] is v2 (current), history[1] is v1 (superseded)
    assert len(history) == 2

    v1 = history[1]  # Older record
    v2 = history[0]  # Current record

    assert v1["company_name"] == "Novo Nordisk"
    assert v2["company_name"] == "Novo Nordisk A/S"

    # Query at exactly v1's valid_from - record is valid starting at this time
    v1_valid_from = datetime.fromisoformat(v1["valid_from"])
    response = await client.get(
        f"/api/companies/{sample_company['company_id']}/at/{v1_valid_from.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Novo Nordisk"

    # Query at current time (should return v2)
    current_time = datetime.utcnow() + timedelta(seconds=1)
    response = await client.get(
        f"/api/companies/{sample_company['company_id']}/at/{current_time.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Novo Nordisk A/S"


@pytest.mark.asyncio
async def test_point_in_time_query_not_found(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test point-in-time query before record exists returns 404."""
    # Time before any records
    past_time = datetime.utcnow() - timedelta(days=1)

    # Create company
    await client.post("/api/companies", json=sample_company)

    # Query at past time should return 404
    response = await client.get(
        f"/api/companies/{sample_company['company_id']}/at/{past_time.isoformat()}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_history_shows_all_versions(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test that history shows all versions in correct order."""
    # Create v1
    await client.post("/api/companies", json=sample_company)

    # Create v2
    v2 = sample_company.copy()
    v2["company_name"] = "Version 2"
    await client.post("/api/companies", json=v2)

    # Create v3
    v3 = sample_company.copy()
    v3["company_name"] = "Version 3"
    await client.post("/api/companies", json=v3)

    # Get history
    response = await client.get(
        f"/api/companies/{sample_company['company_id']}/history"
    )
    history = response.json()

    assert len(history) == 3

    # Most recent first (descending)
    assert history[0]["company_name"] == "Version 3"
    assert history[0]["is_current"] is True
    assert history[0]["valid_to"] is None

    assert history[1]["company_name"] == "Version 2"
    assert history[1]["is_current"] is False
    assert history[1]["valid_to"] is not None

    assert history[2]["company_name"] == "Novo Nordisk"
    assert history[2]["is_current"] is False
    assert history[2]["valid_to"] is not None


@pytest.mark.asyncio
async def test_current_state_only_returns_latest(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test that current state queries only return is_current=True records."""
    # Create multiple versions
    await client.post("/api/companies", json=sample_company)

    v2 = sample_company.copy()
    v2["company_name"] = "Version 2"
    await client.post("/api/companies", json=v2)

    v3 = sample_company.copy()
    v3["company_name"] = "Version 3"
    await client.post("/api/companies", json=v3)

    # Get current should return only v3
    response = await client.get(f"/api/companies/{sample_company['company_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Version 3"

    # List should return only one record per company
    response = await client.get("/api/companies")
    companies = response.json()
    assert len(companies) == 1
    assert companies[0]["company_name"] == "Version 3"


@pytest.mark.asyncio
async def test_point_in_time_query_product(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    """Test point-in-time query for product."""
    # Create initial record
    await client.post("/api/products", json=sample_product)
    time_after_v1 = datetime.utcnow()

    await asyncio.sleep(0.1)

    # Update product
    updated = sample_product.copy()
    updated["class_level_3"] = "Updated Product Name"
    await client.post("/api/products", json=updated)

    # Query at time after v1
    response = await client.get(
        f"/api/products/{sample_product['product_class_3_id']}/at/{time_after_v1.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["class_level_3"] == sample_product["class_level_3"]


@pytest.mark.asyncio
async def test_multiple_entities_history(client: AsyncClient) -> None:
    """Test that history is tracked separately for different entities."""
    # Create two companies
    company1 = {
        "company_id": 1,
        "company_name": "Company A",
        "percentage_a": "0.1000",
    }
    company2 = {
        "company_id": 2,
        "company_name": "Company B",
        "percentage_a": "0.2000",
    }

    await client.post("/api/companies", json=company1)
    await client.post("/api/companies", json=company2)

    # Update company 1 twice
    company1_v2 = company1.copy()
    company1_v2["company_name"] = "Company A v2"
    await client.post("/api/companies", json=company1_v2)

    company1_v3 = company1.copy()
    company1_v3["company_name"] = "Company A v3"
    await client.post("/api/companies", json=company1_v3)

    # Company 1 should have 3 history entries
    response = await client.get("/api/companies/1/history")
    history1 = response.json()
    assert len(history1) == 3

    # Company 2 should have 1 history entry
    response = await client.get("/api/companies/2/history")
    history2 = response.json()
    assert len(history2) == 1

    # List should show 2 current companies
    response = await client.get("/api/companies")
    companies = response.json()
    assert len(companies) == 2
