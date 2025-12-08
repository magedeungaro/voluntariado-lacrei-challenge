from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Endpoint de verificação de saúde para load balancers e monitoramento."""

    @extend_schema(exclude=True)
    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
