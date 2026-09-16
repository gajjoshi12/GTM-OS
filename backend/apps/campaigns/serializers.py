from rest_framework import serializers

from .models import BudgetAllocation, Campaign, ContentItem, Creative, LandingPage, SEOKeyword


class CreativeSerializer(serializers.ModelSerializer):
    ctr = serializers.FloatField(read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    channel = serializers.CharField(source="campaign.channel", read_only=True)

    class Meta:
        model = Creative
        exclude = ("workspace",)


class CampaignSerializer(serializers.ModelSerializer):
    ctr = serializers.FloatField(read_only=True)
    cac = serializers.FloatField(read_only=True)
    roas = serializers.FloatField(read_only=True)
    creatives_count = serializers.IntegerField(read_only=True, default=0)
    landing_page_name = serializers.CharField(source="landing_page.name", read_only=True, default="")

    class Meta:
        model = Campaign
        exclude = ("workspace",)


class CampaignDetailSerializer(CampaignSerializer):
    creatives = CreativeSerializer(many=True, read_only=True)


class BudgetAllocationSerializer(serializers.ModelSerializer):
    delta_pct = serializers.FloatField(read_only=True)

    class Meta:
        model = BudgetAllocation
        exclude = ("workspace",)


class LandingPageSerializer(serializers.ModelSerializer):
    conversion_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = LandingPage
        exclude = ("workspace",)


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        exclude = ("workspace",)


class SEOKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOKeyword
        exclude = ("workspace",)
