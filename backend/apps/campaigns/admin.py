from django.contrib import admin

from .models import BudgetAllocation, Campaign, ContentItem, Creative, LandingPage, SEOKeyword

admin.site.register([Campaign, Creative, BudgetAllocation, LandingPage, ContentItem, SEOKeyword])
