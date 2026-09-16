from rest_framework import serializers

from .models import Competitor, KnowledgeEntity, MarketSignal


class KnowledgeEntitySerializer(serializers.ModelSerializer):
    related_ids = serializers.PrimaryKeyRelatedField(source="related", many=True, read_only=True)

    class Meta:
        model = KnowledgeEntity
        fields = ("id", "kind", "name", "summary", "attributes", "related_ids", "source", "confidence", "freshness", "updated_at")


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        exclude = ("workspace",)


class MarketSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSignal
        exclude = ("workspace",)
