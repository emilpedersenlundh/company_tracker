"""Tests for metrics endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_metric(client: AsyncClient, sample_metric: dict[str, Any]) -> None:
    """Test creating a new metric."""
    response = await client.post("/api/metrics", json=sample_metric)

    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    assert data["company_id"] == sample_metric["company_id"]
    assert data["country_code"] == sample_metric["country_code"]
    assert data["year"] == sample_metric["year"]


@pytest.mark.asyncio
async def test_upsert_metric_no_change(
    client: AsyncClient, sample_metric: dict[str, Any]
) -> None:
    """Test upsert with no data change."""
    response1 = await client.post("/api/metrics", json=sample_metric)
    data1 = response1.json()

    response2 = await client.post("/api/metrics", json=sample_metric)
    data2 = response2.json()

    assert data2["is_new"] is False
    assert data2["record_id"] == data1["record_id"]


@pytest.mark.asyncio
async def test_upsert_metric_with_change(
    client: AsyncClient, sample_metric: dict[str, Any]
) -> None:
    """Test upsert with data change."""
    response1 = await client.post("/api/metrics", json=sample_metric)
    data1 = response1.json()

    updated = sample_metric.copy()
    updated["revenue"] = "160000000.00"

    response2 = await client.post("/api/metrics", json=updated)
    data2 = response2.json()

    assert data2["is_new"] is True
    assert data2["record_id"] != data1["record_id"]


@pytest.mark.asyncio
async def test_list_metrics_with_filters(
    client: AsyncClient, sample_metric: dict[str, Any]
) -> None:
    """Test listing metrics with filters."""
    await client.post("/api/metrics", json=sample_metric)

    metric2 = sample_metric.copy()
    metric2["country_code"] = "US"
    await client.post("/api/metrics", json=metric2)

    # Filter by country
    response = await client.get("/api/metrics", params={"country_code": "DK"})
    assert response.status_code == 200
    metrics = response.json()
    assert len(metrics) == 1
    assert metrics[0]["country_code"] == "DK"


@pytest.mark.asyncio
async def test_get_specific_metric(
    client: AsyncClient, sample_metric: dict[str, Any]
) -> None:
    """Test getting a specific metric by business key."""
    await client.post("/api/metrics", json=sample_metric)

    response = await client.get(
        f"/api/metrics/{sample_metric['company_id']}/{sample_metric['country_code']}/{sample_metric['year']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == sample_metric["company_id"]


@pytest.mark.asyncio
async def test_get_company_metrics(
    client: AsyncClient, sample_metric: dict[str, Any]
) -> None:
    """Test getting all metrics for a company."""
    await client.post("/api/metrics", json=sample_metric)

    metric2 = sample_metric.copy()
    metric2["year"] = 2023
    await client.post("/api/metrics", json=metric2)

    response = await client.get(f"/api/companies/{sample_metric['company_id']}/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert len(metrics) == 2
