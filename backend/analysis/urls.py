from django.urls import path

from .views import AnalysisListView

urlpatterns = [
    path("analysis", AnalysisListView.as_view(), name="analysis-list"),
]
