from rest_framework import serializers

from app.professionals.models import Professional
from app.professionals.serializers import ProfessionalSerializer

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializador para o modelo de Consulta."""

    professional_uuid = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Professional.objects.all(),
        source="professional",
    )

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "date",
            "professional_uuid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Serializador para Consulta com detalhes do Profissional."""

    professional = ProfessionalSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "date",
            "professional",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]
