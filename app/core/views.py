from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Endpoint de verificação de saúde para load balancers e monitoramento."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(exclude=True)
    def get(self, request: Request) -> Response:
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
