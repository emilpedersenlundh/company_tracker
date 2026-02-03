"""Tests for company endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_company(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test creating a new company."""
    response = await client.post("/api/companies", json=sample_company)

    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    assert data["company_id"] == sample_company["company_id"]
    assert "record_id" in data


@pytest.mark.asyncio
async def test_upsert_no_change(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test upsert with no data change returns existing record."""
    # Create initial record
    response1 = await client.post("/api/companies", json=sample_company)
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["is_new"] is True

    # Upsert with same data
    response2 = await client.post("/api/companies", json=sample_company)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["is_new"] is False
    assert data2["record_id"] == data1["record_id"]


@pytest.mark.asyncio
async def test_upsert_with_change(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test upsert with data change creates new record."""
    # Create initial record
    response1 = await client.post("/api/companies", json=sample_company)
    assert response1.status_code == 200
    data1 = response1.json()

    # Update company name
    updated_company = sample_company.copy()
    updated_company["company_name"] = "Novo Nordisk A/S"

    response2 = await client.post("/api/companies", json=updated_company)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["is_new"] is True
    assert data2["record_id"] != data1["record_id"]


@pytest.mark.asyncio
async def test_list_companies(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test listing companies returns only current records."""
    # Create two companies
    await client.post("/api/companies", json=sample_company)

    company2 = sample_company.copy()
    company2["company_id"] = 2
    company2["company_name"] = "Coloplast"
    await client.post("/api/companies", json=company2)

    # List companies
    response = await client.get("/api/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 2


@pytest.mark.asyncio
async def test_get_company(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test getting a specific company."""
    await client.post("/api/companies", json=sample_company)

    response = await client.get(f"/api/companies/{sample_company['company_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == sample_company["company_name"]


@pytest.mark.asyncio
async def test_get_company_not_found(client: AsyncClient) -> None:
    """Test getting non-existent company returns 404."""
    response = await client.get("/api/companies/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_company_history(client: AsyncClient, sample_company: dict[str, Any]) -> None:
    """Test getting company history returns all versions."""
    # Create initial record
    await client.post("/api/companies", json=sample_company)

    # Update company
    updated = sample_company.copy()
    updated["company_name"] = "Novo Nordisk A/S"
    await client.post("/api/companies", json=updated)

    # Get history
    response = await client.get(f"/api/companies/{sample_company['company_id']}/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2

    # Most recent first
    assert history[0]["company_name"] == "Novo Nordisk A/S"
    assert history[0]["is_current"] is True
    assert history[1]["company_name"] == "Novo Nordisk"
    assert history[1]["is_current"] is False


@pytest.mark.asyncio
async def test_search_companies_by_name(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test searching companies by name."""
    await client.post("/api/companies", json=sample_company)

    company2 = sample_company.copy()
    company2["company_id"] = 2
    company2["company_name"] = "Coloplast"
    await client.post("/api/companies", json=company2)

    # Search by partial name
    response = await client.get("/api/companies", params={"name": "Novo"})
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 1
    assert companies[0]["company_name"] == "Novo Nordisk"


@pytest.mark.asyncio
async def test_upsert_with_user_header(
    client: AsyncClient, sample_company: dict[str, Any]
) -> None:
    """Test upsert tracks created_by from header."""
    response = await client.post(
        "/api/companies",
        json=sample_company,
        headers={"X-User": "test@example.com"},
    )
    assert response.status_code == 200

    # Get history to check created_by
    history_response = await client.get(
        f"/api/companies/{sample_company['company_id']}/history"
    )
    history = history_response.json()
    assert history[0]["created_by"] == "test@example.com"
