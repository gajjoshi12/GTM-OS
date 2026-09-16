from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    from ai.client import llm

    status = llm.status()
    return JsonResponse({
        "status": "ok",
        "service": "ai-gtm-os",
        "ai_mode": "live" if status["live"] else "simulation",
        **status,
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/core/", include("apps.core.urls")),
    path("api/agents/", include("apps.agents.urls")),
    path("api/knowledge/", include("apps.knowledge.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/outbound/", include("apps.outbound.urls")),
    path("api/campaigns/", include("apps.campaigns.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/integrations/", include("apps.integrations.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
