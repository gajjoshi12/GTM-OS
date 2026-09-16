from django.contrib import admin

from .models import BrandGuidelines, BusinessProfile, ControlSettings

admin.site.register([BusinessProfile, ControlSettings, BrandGuidelines])
