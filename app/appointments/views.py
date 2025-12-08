from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Appointment
from .serializers import AppointmentDetailSerializer, AppointmentSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar consultas",
        description="Retorna uma lista paginada de todas as consultas. "
        "Pode ser filtrada pelo parâmetro professional_uuid.",
        parameters=[
            OpenApiParameter(
                name="professional_uuid",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filtrar consultas pelo UUID do profissional",
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Obter detalhes da consulta",
        description="Retorna os detalhes de uma consulta específica com informações do profissional.",
    ),
    create=extend_schema(
        summary="Criar consulta",
        description="Cria uma nova consulta vinculada a um profissional.",
    ),
    update=extend_schema(
        summary="Atualizar consulta",
        description="Atualiza todos os campos de uma consulta.",
    ),
    partial_update=extend_schema(
        summary="Atualizar parcialmente consulta",
        description="Atualiza campos específicos de uma consulta.",
    ),
    destroy=extend_schema(
        summary="Excluir consulta",
        description="Exclui uma consulta.",
    ),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Consultas.

    Suporta filtro por professional_uuid via query parameter.
    """

    queryset = Appointment.objects.select_related("professional").all()
    lookup_field = "uuid"

    def get_serializer_class(self):
        """Usa serializador detalhado para retrieve, list usa básico."""
        if self.action in ["retrieve", "list"]:
            return AppointmentDetailSerializer
        return AppointmentSerializer

    def get_queryset(self):
        """Filtra por professional_uuid se fornecido."""
        queryset = super().get_queryset()
        professional_uuid = self.request.query_params.get("professional_uuid")
        if professional_uuid:
            queryset = queryset.filter(professional__uuid=professional_uuid)
        return queryset
