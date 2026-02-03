"""Tests for product shares endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_share(client: AsyncClient, sample_share: dict[str, Any]) -> None:
    """Test creating a new share."""
    response = await client.post("/api/shares", json=sample_share)

    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    assert data["company_id"] == sample_share["company_id"]


@pytest.mark.asyncio
async def test_upsert_share_no_change(
    client: AsyncClient, sample_share: dict[str, Any]
) -> None:
    """Test upsert with no data change."""
    response1 = await client.post("/api/shares", json=sample_share)
    data1 = response1.json()

    response2 = await client.post("/api/shares", json=sample_share)
    data2 = response2.json()

    assert data2["is_new"] is False
    assert data2["record_id"] == data1["record_id"]


@pytest.mark.asyncio
async def test_upsert_share_with_change(
    client: AsyncClient, sample_share: dict[str, Any]
) -> None:
    """Test upsert with data change."""
    response1 = await client.post("/api/shares", json=sample_share)
    data1 = response1.json()

    updated = sample_share.copy()
    updated["share_percentage"] = "0.3500"

    response2 = await client.post("/api/shares", json=updated)
    data2 = response2.json()

    assert data2["is_new"] is True
    assert data2["record_id"] != data1["record_id"]


@pytest.mark.asyncio
async def test_list_shares(client: AsyncClient, sample_share: dict[str, Any]) -> None:
    """Test listing shares."""
    await client.post("/api/shares", json=sample_share)

    share2 = sample_share.copy()
    share2["product_class_3_id"] = 102
    await client.post("/api/shares", json=share2)

    response = await client.get("/api/shares")
    assert response.status_code == 200
    shares = response.json()
    assert len(shares) == 2


@pytest.mark.asyncio
async def test_list_shares_with_filters(
    client: AsyncClient, sample_share: dict[str, Any]
) -> None:
    """Test listing shares with filters."""
    await client.post("/api/shares", json=sample_share)

    share2 = sample_share.copy()
    share2["country_code"] = "US"
    await client.post("/api/shares", json=share2)

    response = await client.get("/api/shares", params={"country_code": "DK"})
    shares = response.json()
    assert len(shares) == 1
    assert shares[0]["country_code"] == "DK"


@pytest.mark.asyncio
async def test_get_company_shares(
    client: AsyncClient, sample_share: dict[str, Any]
) -> None:
    """Test getting all shares for a company."""
    await client.post("/api/shares", json=sample_share)

    share2 = sample_share.copy()
    share2["product_class_3_id"] = 102
    await client.post("/api/shares", json=share2)

    response = await client.get(f"/api/companies/{sample_share['company_id']}/shares")
    assert response.status_code == 200
    shares = response.json()
    assert len(shares) == 2


@pytest.mark.asyncio
async def test_market_share_report(
    client: AsyncClient, sample_share: dict[str, Any]
) -> None:
    """Test market share report aggregation."""
    await client.post("/api/shares", json=sample_share)

    share2 = sample_share.copy()
    share2["product_class_3_id"] = 102
    share2["share_percentage"] = "0.2000"
    await client.post("/api/shares", json=share2)

    response = await client.get("/api/reports/market-share")
    assert response.status_code == 200
    report = response.json()
    assert len(report) == 1
    assert report[0]["company_id"] == sample_share["company_id"]
    assert report[0]["product_count"] == 2
    # 0.325 + 0.20 = 0.525
    assert abs(report[0]["total_share"] - 0.525) < 0.001
