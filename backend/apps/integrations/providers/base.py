"""
Provider adapter interface.

Every capability (ad buying, enrichment, sending...) is called through an adapter
that implements `test_connection()` and capability methods. Adapters receive the
merged credential dict (UI-stored credentials win over .env).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class HealthResult:
    ok: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    simulated: bool = False


class BaseAdapter:
    key: str = ""
    env_map: dict[str, str] = {}  # field -> env var name
    timeout = 10

    def __init__(self, credentials: dict | None = None, config: dict | None = None):
        self.config = config or {}
        merged = {f: os.environ.get(v, "") for f, v in self.env_map.items()}
        merged.update({k: v for k, v in (credentials or {}).items() if v})
        self.creds = merged

    @property
    def configured(self) -> bool:
        required = getattr(self, "required", list(self.env_map))
        return all(self.creds.get(f) for f in required)

    def test_connection(self) -> HealthResult:
        if not self.configured:
            return HealthResult(False, "Not configured - running in simulation mode", simulated=True)
        try:
            return self._ping()
        except requests.RequestException as exc:
            return HealthResult(False, f"Network error: {exc}")
        except Exception as exc:  # noqa: BLE001
            return HealthResult(False, f"Error: {exc}")

    def _ping(self) -> HealthResult:  # override
        return HealthResult(True, "Credentials present (no live ping implemented)")

    def _get(self, url: str, **kw) -> requests.Response:
        kw.setdefault("timeout", self.timeout)
        return requests.get(url, **kw)
