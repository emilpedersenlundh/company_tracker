"""Tests for product hierarchy endpoints."""

from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, sample_product: dict[str, Any]) -> None:
    """Test creating a new product hierarchy."""
    response = await client.post("/api/products", json=sample_product)

    assert response.status_code == 200
    data = response.json()
    assert data["is_new"] is True
    assert data["product_class_3_id"] == sample_product["product_class_3_id"]


@pytest.mark.asyncio
async def test_upsert_product_no_change(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    """Test upsert with no data change."""
    response1 = await client.post("/api/products", json=sample_product)
    data1 = response1.json()

    response2 = await client.post("/api/products", json=sample_product)
    data2 = response2.json()

    assert data2["is_new"] is False
    assert data2["record_id"] == data1["record_id"]


@pytest.mark.asyncio
async def test_upsert_product_with_change(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    """Test upsert with data change."""
    response1 = await client.post("/api/products", json=sample_product)
    data1 = response1.json()

    updated = sample_product.copy()
    updated["class_level_3"] = "Advanced Blood Glucose Monitors"

    response2 = await client.post("/api/products", json=updated)
    data2 = response2.json()

    assert data2["is_new"] is True
    assert data2["record_id"] != data1["record_id"]


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, sample_product: dict[str, Any]) -> None:
    """Test listing products."""
    await client.post("/api/products", json=sample_product)

    product2 = sample_product.copy()
    product2["product_class_3_id"] = 102
    product2["class_level_3"] = "Insulin Pumps"
    await client.post("/api/products", json=product2)

    response = await client.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 2


@pytest.mark.asyncio
async def test_list_products_with_filters(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    """Test listing products with filters."""
    await client.post("/api/products", json=sample_product)

    product2 = sample_product.copy()
    product2["product_class_3_id"] = 102
    product2["class_level_1"] = "Pharmaceuticals"
    product2["class_level_2"] = "Diabetes"
    product2["class_level_3"] = "Insulin"
    await client.post("/api/products", json=product2)

    # Filter by level 1
    response = await client.get(
        "/api/products", params={"class_level_1": "Medical Devices"}
    )
    products = response.json()
    assert len(products) == 1
    assert products[0]["class_level_1"] == "Medical Devices"


@pytest.mark.asyncio
async def test_get_product(client: AsyncClient, sample_product: dict[str, Any]) -> None:
    """Test getting a specific product."""
    await client.post("/api/products", json=sample_product)

    response = await client.get(
        f"/api/products/{sample_product['product_class_3_id']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["class_level_3"] == sample_product["class_level_3"]


@pytest.mark.asyncio
async def test_get_product_history(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    """Test getting product history."""
    await client.post("/api/products", json=sample_product)

    updated = sample_product.copy()
    updated["class_level_3"] = "Advanced BGM"
    await client.post("/api/products", json=updated)

    response = await client.get(
        f"/api/products/{sample_product['product_class_3_id']}/history"
    )
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
