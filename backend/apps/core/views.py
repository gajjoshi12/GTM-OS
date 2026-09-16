from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agents import orchestrator
from apps.agents.models import AgentRun

from .models import BrandGuidelines, BusinessProfile, ControlSettings
from .serializers import (BrandGuidelinesSerializer, BusinessProfileSerializer, ControlSettingsSerializer,
                          OnboardingSerializer)
from .workspace import get_workspace


class _SingletonView(APIView):
    model = None
    serializer_class = None

    def _obj(self, request):
        ws = get_workspace(request)
        obj, _ = self.model.objects.get_or_create(workspace=ws, defaults=self.defaults(ws))
        return obj

    def defaults(self, ws):
        return {}

    def get(self, request):
        return Response(self.serializer_class(self._obj(request)).data)

    def patch(self, request):
        ser = self.serializer_class(self._obj(request), data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class BusinessProfileView(_SingletonView):
    model = BusinessProfile
    serializer_class = BusinessProfileSerializer

    def defaults(self, ws):
        return {"company_name": ws.name}


class ControlSettingsView(_SingletonView):
    model = ControlSettings
    serializer_class = ControlSettingsSerializer


class BrandGuidelinesView(_SingletonView):
    model = BrandGuidelines
    serializer_class = BrandGuidelinesSerializer


class OnboardingView(APIView):
    """Founder sentence in -> derived GTM plan out (spec 1.2 / 1.3). Kicks off the intelligence agents."""

    def post(self, request):
        ws = get_workspace(request)
        ser = OnboardingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        business, _ = BusinessProfile.objects.update_or_create(workspace=ws, defaults=data)
        orchestrator.ensure_settings(ws)
        orchestrator.ensure_agents(ws)

        business.derived_plan = orchestrator.derive_plan(business)
        business.plan_generated_at = timezone.now()
        business.save()

        ws.name = business.company_name
        ws.onboarding_completed = True
        ws.save(update_fields=["name", "onboarding_completed"])

        runs = [orchestrator.run_agent(ws, k, {"task": "onboarding"}, trigger=AgentRun.Trigger.CMO)
                for k in ("business_intelligence", "market_intelligence", "competitor_intelligence", "icp", "cmo")]
        return Response({
            "business": BusinessProfileSerializer(business).data,
            "runs": [{"agent": r.agent.key, "status": r.status, "summary": r.summary} for r in runs],
        }, status=status.HTTP_201_CREATED)


class RegeneratePlanView(APIView):
    def post(self, request):
        ws = get_workspace(request)
        business = BusinessProfile.objects.filter(workspace=ws).first()
        if not business:
            return Response({"detail": "Complete onboarding first."}, status=400)
        business.derived_plan = orchestrator.derive_plan(business)
        business.plan_generated_at = timezone.now()
        business.save()
        return Response(BusinessProfileSerializer(business).data)
