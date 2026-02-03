"""HTTP client for Company Tracker API."""

import httpx
from typing import Any
from datetime import datetime


class CompanyTrackerClient:
    """Synchronous client for the Company Tracker API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.user = "streamlit-user"
        self.timeout = 30.0

    def _headers(self) -> dict[str, str]:
        return {"X-User": self.user}

    def set_user(self, user: str) -> None:
        """Set the user for audit tracking."""
        self.user = user

    # Health check
    def health_check(self) -> bool:
        """Check if the API is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False

    # Companies
    def list_companies(
        self, name: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List all current companies."""
        with httpx.Client(timeout=self.timeout) as client:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if name:
                params["name"] = name
            resp = client.get(f"{self.base_url}/api/companies", params=params)
            resp.raise_for_status()
            return resp.json()

    def get_company(self, company_id: int) -> dict[str, Any] | None:
        """Get a company by ID."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/companies/{company_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    def get_company_history(self, company_id: int) -> list[dict[str, Any]]:
        """Get full history for a company."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/companies/{company_id}/history")
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return resp.json()

    def get_company_at_time(
        self, company_id: int, point_in_time: datetime
    ) -> dict[str, Any] | None:
        """Get company state at a specific point in time."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                f"{self.base_url}/api/companies/{company_id}/at/{point_in_time.isoformat()}"
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    def upsert_company(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create or update a company."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/companies",
                json=data,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # Metrics
    def list_metrics(
        self,
        company_id: int | None = None,
        country_code: str | None = None,
        year: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List metrics with optional filters."""
        with httpx.Client(timeout=self.timeout) as client:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if company_id is not None:
                params["company_id"] = company_id
            if country_code:
                params["country_code"] = country_code
            if year is not None:
                params["year"] = year
            resp = client.get(f"{self.base_url}/api/metrics", params=params)
            resp.raise_for_status()
            return resp.json()

    def get_company_metrics(self, company_id: int) -> list[dict[str, Any]]:
        """Get all metrics for a company."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/companies/{company_id}/metrics")
            resp.raise_for_status()
            return resp.json()

    def upsert_metric(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create or update a metric."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/metrics",
                json=data,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # Products
    def list_products(
        self,
        class_level_1: str | None = None,
        class_level_2: str | None = None,
        name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List products with optional filters."""
        with httpx.Client(timeout=self.timeout) as client:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if class_level_1:
                params["class_level_1"] = class_level_1
            if class_level_2:
                params["class_level_2"] = class_level_2
            if name:
                params["name"] = name
            resp = client.get(f"{self.base_url}/api/products", params=params)
            resp.raise_for_status()
            return resp.json()

    def get_product(self, product_class_3_id: int) -> dict[str, Any] | None:
        """Get a product by ID."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/products/{product_class_3_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    def get_product_history(self, product_class_3_id: int) -> list[dict[str, Any]]:
        """Get full history for a product."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                f"{self.base_url}/api/products/{product_class_3_id}/history"
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            return resp.json()

    def upsert_product(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create or update a product."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/products",
                json=data,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # Shares
    def list_shares(
        self,
        company_id: int | None = None,
        country_code: str | None = None,
        product_class_3_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List shares with optional filters."""
        with httpx.Client(timeout=self.timeout) as client:
            params: dict[str, Any] = {"limit": limit, "offset": offset}
            if company_id is not None:
                params["company_id"] = company_id
            if country_code:
                params["country_code"] = country_code
            if product_class_3_id is not None:
                params["product_class_3_id"] = product_class_3_id
            resp = client.get(f"{self.base_url}/api/shares", params=params)
            resp.raise_for_status()
            return resp.json()

    def get_company_shares(self, company_id: int) -> list[dict[str, Any]]:
        """Get all shares for a company."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(f"{self.base_url}/api/companies/{company_id}/shares")
            resp.raise_for_status()
            return resp.json()

    def upsert_share(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create or update a share."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/api/shares",
                json=data,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    # Reports
    def get_market_share_report(
        self,
        country_code: str | None = None,
        product_class_3_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get aggregated market share report."""
        with httpx.Client(timeout=self.timeout) as client:
            params: dict[str, Any] = {}
            if country_code:
                params["country_code"] = country_code
            if product_class_3_id is not None:
                params["product_class_3_id"] = product_class_3_id
            resp = client.get(f"{self.base_url}/api/reports/market-share", params=params)
            resp.raise_for_status()
            return resp.json()


# Singleton instance
_client: CompanyTrackerClient | None = None


def get_client(base_url: str = "http://localhost:8000") -> CompanyTrackerClient:
    """Get or create the API client singleton."""
    global _client
    if _client is None or _client.base_url != base_url:
        _client = CompanyTrackerClient(base_url)
    return _client
