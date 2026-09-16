from django.urls import path

from .views import ConnectorDetailView, ConnectorListView, ConnectorTestView

urlpatterns = [
    path("", ConnectorListView.as_view()),
    path("<slug:key>/", ConnectorDetailView.as_view()),
    path("<slug:key>/test/", ConnectorTestView.as_view()),
]
