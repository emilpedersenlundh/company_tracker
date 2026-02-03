#!/usr/bin/env python3
"""Seed database with sample data for testing."""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import async_session_factory
from app.repositories import (
    CompanyRepository,
    MetricsRepository,
    ProductRepository,
    SharesRepository,
)


async def seed_companies(session) -> None:
    """Seed company data."""
    repo = CompanyRepository(session)

    companies = [
        {
            "company_id": 1,
            "company_name": "Novo Nordisk",
            "percentage_a": Decimal("0.2500"),
            "percentage_b": Decimal("0.3500"),
            "percentage_c": Decimal("0.4000"),
        },
        {
            "company_id": 2,
            "company_name": "Coloplast",
            "percentage_a": Decimal("0.3000"),
            "percentage_b": Decimal("0.3000"),
            "percentage_c": Decimal("0.4000"),
        },
        {
            "company_id": 3,
            "company_name": "Medtronic",
            "percentage_a": Decimal("0.2000"),
            "percentage_b": Decimal("0.4000"),
            "percentage_c": Decimal("0.4000"),
        },
        {
            "company_id": 4,
            "company_name": "Abbott Laboratories",
            "percentage_a": Decimal("0.2800"),
            "percentage_b": Decimal("0.3200"),
            "percentage_c": Decimal("0.4000"),
        },
    ]

    for company in companies:
        record_id, is_new = await repo.upsert_company(
            company_id=company["company_id"],
            company_name=company["company_name"],
            percentage_a=company["percentage_a"],
            percentage_b=company["percentage_b"],
            percentage_c=company["percentage_c"],
            created_by="seed_script",
        )
        status = "created" if is_new else "exists"
        print(f"Company {company['company_name']}: {status} (record_id={record_id})")


async def seed_metrics(session) -> None:
    """Seed metrics data."""
    repo = MetricsRepository(session)

    metrics = [
        {
            "company_id": 1,
            "country_code": "DK",
            "year": 2024,
            "revenue": Decimal("150000000.00"),
            "gross_profit": Decimal("85000000.00"),
            "headcount": 5200,
        },
        {
            "company_id": 1,
            "country_code": "US",
            "year": 2024,
            "revenue": Decimal("280000000.00"),
            "gross_profit": Decimal("145000000.00"),
            "headcount": 8500,
        },
        {
            "company_id": 2,
            "country_code": "DK",
            "year": 2024,
            "revenue": Decimal("95000000.00"),
            "gross_profit": Decimal("52000000.00"),
            "headcount": 2800,
        },
        {
            "company_id": 3,
            "country_code": "US",
            "year": 2024,
            "revenue": Decimal("320000000.00"),
            "gross_profit": Decimal("175000000.00"),
            "headcount": 12000,
        },
    ]

    for metric in metrics:
        record_id, is_new = await repo.upsert_metric(
            company_id=metric["company_id"],
            country_code=metric["country_code"],
            year=metric["year"],
            revenue=metric["revenue"],
            gross_profit=metric["gross_profit"],
            headcount=metric["headcount"],
            created_by="seed_script",
        )
        status = "created" if is_new else "exists"
        print(
            f"Metric {metric['company_id']}/{metric['country_code']}/{metric['year']}: "
            f"{status} (record_id={record_id})"
        )


async def seed_products(session) -> None:
    """Seed product hierarchy data."""
    repo = ProductRepository(session)

    products = [
        {
            "product_class_3_id": 101,
            "class_level_1": "Medical Devices",
            "class_level_2": "Diagnostic Equipment",
            "class_level_3": "Blood Glucose Monitors",
        },
        {
            "product_class_3_id": 102,
            "class_level_1": "Medical Devices",
            "class_level_2": "Therapeutic Equipment",
            "class_level_3": "Insulin Pumps",
        },
        {
            "product_class_3_id": 103,
            "class_level_1": "Medical Devices",
            "class_level_2": "Wound Care",
            "class_level_3": "Ostomy Bags",
        },
        {
            "product_class_3_id": 201,
            "class_level_1": "Pharmaceuticals",
            "class_level_2": "Diabetes",
            "class_level_3": "GLP-1 Agonists",
        },
        {
            "product_class_3_id": 202,
            "class_level_1": "Pharmaceuticals",
            "class_level_2": "Diabetes",
            "class_level_3": "Insulin Analogs",
        },
    ]

    for product in products:
        record_id, is_new = await repo.upsert_product(
            product_class_3_id=product["product_class_3_id"],
            class_level_1=product["class_level_1"],
            class_level_2=product["class_level_2"],
            class_level_3=product["class_level_3"],
            created_by="seed_script",
        )
        status = "created" if is_new else "exists"
        print(
            f"Product {product['product_class_3_id']} ({product['class_level_3']}): "
            f"{status} (record_id={record_id})"
        )


async def seed_shares(session) -> None:
    """Seed product shares data."""
    repo = SharesRepository(session)

    shares = [
        {"company_id": 1, "country_code": "DK", "product_class_3_id": 101, "share_percentage": Decimal("0.3250")},
        {"company_id": 1, "country_code": "DK", "product_class_3_id": 102, "share_percentage": Decimal("0.4500")},
        {"company_id": 1, "country_code": "DK", "product_class_3_id": 201, "share_percentage": Decimal("0.5500")},
        {"company_id": 2, "country_code": "DK", "product_class_3_id": 103, "share_percentage": Decimal("0.6200")},
        {"company_id": 3, "country_code": "US", "product_class_3_id": 102, "share_percentage": Decimal("0.3800")},
        {"company_id": 4, "country_code": "US", "product_class_3_id": 101, "share_percentage": Decimal("0.4200")},
    ]

    for share in shares:
        record_id, is_new = await repo.upsert_share(
            company_id=share["company_id"],
            country_code=share["country_code"],
            product_class_3_id=share["product_class_3_id"],
            share_percentage=share["share_percentage"],
            created_by="seed_script",
        )
        status = "created" if is_new else "exists"
        print(
            f"Share {share['company_id']}/{share['country_code']}/{share['product_class_3_id']}: "
            f"{status} (record_id={record_id})"
        )


async def main() -> None:
    """Run all seed functions."""
    print("Seeding database with sample data...\n")

    async with async_session_factory() as session:
        print("=== Companies ===")
        await seed_companies(session)
        await session.commit()

        print("\n=== Metrics ===")
        await seed_metrics(session)
        await session.commit()

        print("\n=== Products ===")
        await seed_products(session)
        await session.commit()

        print("\n=== Shares ===")
        await seed_shares(session)
        await session.commit()

    print("\nSeeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
