from __future__ import annotations

import json

from django.conf import settings
from django.db import models

from apps.core.workspace import WorkspaceModel


def _fernet():
    key = settings.CREDENTIALS_ENCRYPTION_KEY
    if not key:
        return None
    from cryptography.fernet import Fernet

    return Fernet(key.encode() if isinstance(key, str) else key)


class Connector(WorkspaceModel):
    """A configured provider inside a workspace (connector framework, spec 8)."""

    class Status(models.TextChoices):
        NOT_CONNECTED = "not_connected"
        CONNECTED = "connected"
        SIMULATED = "simulated"
        ERROR = "error"

    provider = models.CharField(max_length=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_CONNECTED)
    account_label = models.CharField(max_length=160, blank=True)
    config = models.JSONField(default=dict, blank=True)  # non-secret settings (account ids, etc.)
    _credentials = models.TextField(blank=True, db_column="credentials")
    health = models.JSONField(default=dict, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta(WorkspaceModel.Meta):
        unique_together = ("workspace", "provider")
        ordering = ("provider",)

    # --- credential handling -------------------------------------------------
    def set_credentials(self, data: dict) -> None:
        raw = json.dumps(data or {})
        f = _fernet()
        self._credentials = f.encrypt(raw.encode()).decode() if f else raw

    def get_credentials(self) -> dict:
        if not self._credentials:
            return {}
        f = _fernet()
        try:
            raw = f.decrypt(self._credentials.encode()).decode() if f else self._credentials
            return json.loads(raw)
        except Exception:
            try:
                return json.loads(self._credentials)
            except Exception:
                return {}

    @property
    def has_credentials(self) -> bool:
        return bool(self._credentials)

    def __str__(self):
        return f"{self.provider} [{self.status}]"
