from django.urls import path

from .views import (
    EntryDetailView,
    EntryListCreateView,
    SourceListCreateView,
    UploadIngestView,
)

urlpatterns = [
    path("sources", SourceListCreateView.as_view(), name="source-list"),
    path("sources/upload", UploadIngestView.as_view(), name="source-upload"),
    path("entries", EntryListCreateView.as_view(), name="entry-list"),
    path("entries/<int:pk>", EntryDetailView.as_view(), name="entry-detail"),
]
