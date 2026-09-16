from rest_framework import serializers

from .models import AttributionTouch, DailyMetric, Experiment, MemoryInsight, RevenueEvent


class DailyMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMetric
        exclude = ("workspace",)


class RevenueEventSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True, default="")

    class Meta:
        model = RevenueEvent
        exclude = ("workspace",)


class AttributionTouchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributionTouch
        exclude = ("workspace",)


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        exclude = ("workspace",)


class MemoryInsightSerializer(serializers.ModelSerializer):
    source_experiment_name = serializers.CharField(source="source_experiment.name", read_only=True, default="")

    class Meta:
        model = MemoryInsight
        exclude = ("workspace",)
