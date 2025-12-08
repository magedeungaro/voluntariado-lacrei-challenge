from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Professional
from .serializers import ProfessionalDetailSerializer, ProfessionalSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar profissionais",
        description="Retorna uma lista paginada de todos os profissionais de saúde.",
    ),
    retrieve=extend_schema(
        summary="Obter detalhes do profissional",
        description="Retorna os detalhes de um profissional de saúde específico.",
    ),
    create=extend_schema(
        summary="Criar profissional",
        description="Cria um novo profissional de saúde com endereço e contatos.",
    ),
    update=extend_schema(
        summary="Atualizar profissional",
        description="Atualiza todos os campos de um profissional de saúde.",
    ),
    partial_update=extend_schema(
        summary="Atualizar parcialmente profissional",
        description="Atualiza campos específicos de um profissional de saúde.",
    ),
    destroy=extend_schema(
        summary="Excluir profissional",
        description="Exclui um profissional de saúde.",
    ),
)
class ProfessionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Profissionais de Saúde.

    Fornece ações de listar, criar, detalhar, atualizar e excluir.
    Endereço e contatos são gerenciados como objetos aninhados.
    """

    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    lookup_field = "uuid"

    def get_serializer_class(self):
        """Usa serializador detalhado para retrieve."""
        if self.action == "retrieve":
            return ProfessionalDetailSerializer
        return ProfessionalSerializer
