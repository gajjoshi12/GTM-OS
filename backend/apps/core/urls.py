from django.urls import path

from .views import BrandGuidelinesView, BusinessProfileView, ControlSettingsView, OnboardingView, RegeneratePlanView

urlpatterns = [
    path("business/", BusinessProfileView.as_view()),
    path("business/regenerate-plan/", RegeneratePlanView.as_view()),
    path("controls/", ControlSettingsView.as_view()),
    path("brand/", BrandGuidelinesView.as_view()),
    path("onboarding/", OnboardingView.as_view()),
]
