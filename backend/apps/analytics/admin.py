from django.contrib import admin

from .models import AttributionTouch, DailyMetric, Experiment, MemoryInsight, RevenueEvent

admin.site.register([DailyMetric, AttributionTouch, RevenueEvent, Experiment, MemoryInsight])
