from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AnalysisRecord
from .serializers import AnalysisRecordSerializer


class AnalysisListView(APIView):
    def get(self, request):
        queryset = AnalysisRecord.objects.filter(tenant=request.user.tenant).order_by("-id")
        serializer = AnalysisRecordSerializer(queryset, many=True)
        return Response({"results": serializer.data})
