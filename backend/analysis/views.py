from rest_framework import generics

from .models import Entry, Source
from .serializers import EntrySerializer, SourceSerializer


class SourceListCreateView(generics.ListCreateAPIView):
    queryset = Source.objects.all().order_by("-id")
    serializer_class = SourceSerializer


class EntryListCreateView(generics.ListCreateAPIView):
    queryset = Entry.objects.select_related(
        "source", "created_by", "approved_by"
    ).order_by("-id")
    serializer_class = EntrySerializer


class EntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entry.objects.select_related(
        "source", "created_by", "approved_by"
    )
    serializer_class = EntrySerializer
