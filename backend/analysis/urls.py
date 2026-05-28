from django.urls import path

from .views import EntryDetailView, EntryListCreateView, SourceListCreateView

urlpatterns = [
    path("sources", SourceListCreateView.as_view(), name="source-list"),
    path("entries", EntryListCreateView.as_view(), name="entry-list"),
    path("entries/<int:pk>", EntryDetailView.as_view(), name="entry-detail"),
]
