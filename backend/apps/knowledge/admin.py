from django.contrib import admin

from .models import Competitor, KnowledgeEntity, MarketSignal

admin.site.register([KnowledgeEntity, Competitor, MarketSignal])
