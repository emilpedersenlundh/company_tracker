"""Initial schema with append-only temporal tables.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Companies History Table
    op.create_table(
        "companies_history",
        sa.Column("record_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("percentage_a", sa.Numeric(5, 4), nullable=True),
        sa.Column("percentage_b", sa.Numeric(5, 4), nullable=True),
        sa.Column("percentage_c", sa.Numeric(5, 4), nullable=True),
        sa.Column(
            "valid_from",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("record_id"),
    )

    # Company Country Metrics History Table
    op.create_table(
        "company_country_metrics_history",
        sa.Column("record_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(3), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("revenue", sa.Numeric(15, 2), nullable=True),
        sa.Column("gross_profit", sa.Numeric(15, 2), nullable=True),
        sa.Column("headcount", sa.Integer(), nullable=True),
        sa.Column(
            "valid_from",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("record_id"),
    )

    # Product Hierarchy History Table
    op.create_table(
        "product_hierarchy_history",
        sa.Column("record_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_class_3_id", sa.Integer(), nullable=False),
        sa.Column("class_level_1", sa.String(100), nullable=True),
        sa.Column("class_level_2", sa.String(100), nullable=True),
        sa.Column("class_level_3", sa.String(100), nullable=True),
        sa.Column(
            "valid_from",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("record_id"),
    )

    # Product Shares History Table
    op.create_table(
        "product_shares_history",
        sa.Column("record_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(3), nullable=False),
        sa.Column("product_class_3_id", sa.Integer(), nullable=False),
        sa.Column("share_percentage", sa.Numeric(5, 4), nullable=True),
        sa.Column(
            "valid_from",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column(
            "is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("record_id"),
    )

    # Create indexes

    # Companies indexes
    op.create_index(
        "idx_companies_current",
        "companies_history",
        ["company_id"],
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "idx_companies_temporal",
        "companies_history",
        ["company_id", sa.text("valid_from DESC"), "valid_to"],
    )

    # Metrics indexes
    op.create_index(
        "idx_metrics_current",
        "company_country_metrics_history",
        ["company_id", "country_code", "year"],
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "idx_metrics_temporal",
        "company_country_metrics_history",
        ["company_id", "country_code", "year", sa.text("valid_from DESC")],
    )

    # Product hierarchy indexes
    op.create_index(
        "idx_product_current",
        "product_hierarchy_history",
        ["product_class_3_id"],
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "idx_product_temporal",
        "product_hierarchy_history",
        ["product_class_3_id", sa.text("valid_from DESC")],
    )

    # Product shares indexes
    op.create_index(
        "idx_shares_current",
        "product_shares_history",
        ["company_id", "country_code", "product_class_3_id"],
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "idx_shares_temporal",
        "product_shares_history",
        ["company_id", "country_code", "product_class_3_id", sa.text("valid_from DESC")],
    )

    # Create current-state views
    op.execute("""
        CREATE VIEW companies_current AS
        SELECT
            company_id,
            company_name,
            percentage_a,
            percentage_b,
            percentage_c,
            valid_from
        FROM companies_history
        WHERE is_current = TRUE
    """)

    op.execute("""
        CREATE VIEW company_country_metrics_current AS
        SELECT
            company_id,
            country_code,
            year,
            revenue,
            gross_profit,
            headcount,
            valid_from
        FROM company_country_metrics_history
        WHERE is_current = TRUE
    """)

    op.execute("""
        CREATE VIEW product_hierarchy_current AS
        SELECT
            product_class_3_id,
            class_level_1,
            class_level_2,
            class_level_3,
            valid_from
        FROM product_hierarchy_history
        WHERE is_current = TRUE
    """)

    op.execute("""
        CREATE VIEW product_shares_current AS
        SELECT
            company_id,
            country_code,
            product_class_3_id,
            share_percentage,
            valid_from
        FROM product_shares_history
        WHERE is_current = TRUE
    """)


def downgrade() -> None:
    # Drop views
    op.execute("DROP VIEW IF EXISTS product_shares_current")
    op.execute("DROP VIEW IF EXISTS product_hierarchy_current")
    op.execute("DROP VIEW IF EXISTS company_country_metrics_current")
    op.execute("DROP VIEW IF EXISTS companies_current")

    # Drop indexes
    op.drop_index("idx_shares_temporal", table_name="product_shares_history")
    op.drop_index("idx_shares_current", table_name="product_shares_history")
    op.drop_index("idx_product_temporal", table_name="product_hierarchy_history")
    op.drop_index("idx_product_current", table_name="product_hierarchy_history")
    op.drop_index("idx_metrics_temporal", table_name="company_country_metrics_history")
    op.drop_index("idx_metrics_current", table_name="company_country_metrics_history")
    op.drop_index("idx_companies_temporal", table_name="companies_history")
    op.drop_index("idx_companies_current", table_name="companies_history")

    # Drop tables
    op.drop_table("product_shares_history")
    op.drop_table("product_hierarchy_history")
    op.drop_table("company_country_metrics_history")
    op.drop_table("companies_history")
