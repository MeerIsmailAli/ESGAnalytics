from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, Entry, Source
from .serializers import EntrySerializer, SourceSerializer, UploadSerializer
from .services import ingest_file


class SourceListCreateView(generics.ListCreateAPIView):
    queryset = Source.objects.all().order_by("-id")
    serializer_class = SourceSerializer


class EntryListCreateView(generics.ListCreateAPIView):
    queryset = Entry.objects.select_related(
        "source", "created_by", "approved_by", "flagged_by"
    ).order_by("-id")
    serializer_class = EntrySerializer


class EntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Entry.objects.select_related(
        "source", "created_by", "approved_by", "flagged_by"
    )
    serializer_class = EntrySerializer

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            entry=instance,
            user=self.request.user,
            action=AuditLog.Action.DELETED,
            note=instance.label[:200],
        )
        instance.delete()


class UploadIngestView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        uploaded = data["file"]
        source_name = data.get("name") or uploaded.name
        file_bytes = uploaded.read()

        result, error = ingest_file(
            source_type=data["source_type"],
            file_bytes=file_bytes,
            source_name=source_name,
            client_name=data["client_name"],
            user=request.user,
            filename=uploaded.name,
        )
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)
