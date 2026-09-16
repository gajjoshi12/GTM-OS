from rest_framework import serializers

from .models import BrandGuidelines, BusinessProfile, ControlSettings


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ("id", "company_name", "website", "industry", "description", "founder_brief", "currency", "revenue_goal",
                  "marketing_budget", "gross_margin_pct", "target_geographies", "business_model", "average_deal_size",
                  "sales_cycle_days", "derived_plan", "plan_generated_at", "updated_at")
        read_only_fields = ("derived_plan", "plan_generated_at")


class ControlSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlSettings
        exclude = ("workspace",)


class BrandGuidelinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandGuidelines
        exclude = ("workspace",)


class OnboardingSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=160)
    website = serializers.URLField(required=False, allow_blank=True)
    industry = serializers.CharField(max_length=120, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    founder_brief = serializers.CharField()
    currency = serializers.CharField(max_length=6, required=False)
    revenue_goal = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    marketing_budget = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    gross_margin_pct = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    target_geographies = serializers.ListField(child=serializers.CharField(), required=False)
    business_model = serializers.CharField(max_length=40, required=False)
    average_deal_size = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    sales_cycle_days = serializers.IntegerField(required=False)
