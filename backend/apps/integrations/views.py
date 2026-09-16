from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.workspace import get_workspace

from .models import Connector
from .providers.adapters import get_adapter
from .registry import CATEGORIES, PROVIDER_BY_KEY, PROVIDERS, env_configured


def _row(provider: dict, connector: Connector | None) -> dict:
    env_ok = env_configured(provider)
    if connector and connector.status == Connector.Status.CONNECTED:
        state = "connected"
    elif connector and connector.status == Connector.Status.ERROR:
        state = "error"
    elif env_ok:
        state = "env_configured"
    else:
        state = "not_connected"
    return {
        **{k: provider[k] for k in ("key", "name", "category", "env_vars", "fields", "docs", "capabilities", "used_by")},
        "category_label": CATEGORIES.get(provider["category"], provider["category"]),
        "state": state,
        "env_configured": env_ok,
        "has_credentials": bool(connector and connector.has_credentials),
        "account_label": connector.account_label if connector else "",
        "config": connector.config if connector else {},
        "health": connector.health if connector else {},
        "last_synced_at": connector.last_synced_at if connector else None,
        "error_message": connector.error_message if connector else "",
    }


class ConnectorListView(APIView):
    def get(self, request):
        ws = get_workspace(request)
        rows = {c.provider: c for c in Connector.objects.filter(workspace=ws)}
        data = [_row(p, rows.get(p["key"])) for p in PROVIDERS]
        connected = sum(1 for d in data if d["state"] in ("connected", "env_configured"))
        return Response({
            "categories": [{"key": k, "label": v} for k, v in CATEGORIES.items()],
            "providers": data,
            "summary": {"total": len(data), "connected": connected, "simulated": len(data) - connected},
        })


class ConnectorDetailView(APIView):
    def _provider(self, key):
        p = PROVIDER_BY_KEY.get(key)
        if not p:
            return None
        return p

    def post(self, request, key):
        """Store credentials (encrypted) + config and test the connection."""
        provider = self._provider(key)
        if not provider:
            return Response({"detail": "Unknown provider"}, status=404)
        ws = get_workspace(request)
        connector, _ = Connector.objects.get_or_create(workspace=ws, provider=key)
        creds = {k: v for k, v in (request.data.get("credentials") or {}).items() if k in provider["fields"]}
        if creds:
            merged = connector.get_credentials()
            merged.update(creds)
            connector.set_credentials(merged)
        connector.config = {**connector.config, **(request.data.get("config") or {})}
        connector.account_label = request.data.get("account_label", connector.account_label)
        result = get_adapter(provider, connector.get_credentials(), connector.config).test_connection()
        connector.health = {"ok": result.ok, "message": result.message, "details": result.details, "checked_at": timezone.now().isoformat()}
        connector.status = Connector.Status.CONNECTED if result.ok else (Connector.Status.SIMULATED if result.simulated else Connector.Status.ERROR)
        connector.error_message = "" if result.ok else result.message
        connector.save()
        return Response(_row(provider, connector), status=status.HTTP_200_OK)

    def delete(self, request, key):
        ws = get_workspace(request)
        Connector.objects.filter(workspace=ws, provider=key).delete()
        provider = self._provider(key)
        return Response(_row(provider, None) if provider else {}, status=200)


class ConnectorTestView(APIView):
    def post(self, request, key):
        provider = PROVIDER_BY_KEY.get(key)
        if not provider:
            return Response({"detail": "Unknown provider"}, status=404)
        ws = get_workspace(request)
        connector = Connector.objects.filter(workspace=ws, provider=key).first()
        creds = connector.get_credentials() if connector else {}
        result = get_adapter(provider, creds, connector.config if connector else {}).test_connection()
        if connector:
            connector.health = {"ok": result.ok, "message": result.message, "details": result.details, "checked_at": timezone.now().isoformat()}
            connector.status = Connector.Status.CONNECTED if result.ok else (Connector.Status.SIMULATED if result.simulated else Connector.Status.ERROR)
            connector.error_message = "" if result.ok else result.message
            connector.last_synced_at = timezone.now() if result.ok else connector.last_synced_at
            connector.save()
        return Response({"ok": result.ok, "message": result.message, "details": result.details, "simulated": result.simulated})
