from typing import Any

from rest_framework import serializers

from .models import Address, Contact, Professional
from .services import ProfessionalService


class AddressSerializer(serializers.ModelSerializer[Address]):
    """Serializador para o modelo de Endereço."""

    class Meta:
        model = Address
        fields = [
            "street",
            "number",
            "neighborhood",
            "complement",
            "city",
            "state",
            "zip_code",
        ]


class ContactSerializer(serializers.ModelSerializer[Contact]):
    """Serializador para o modelo de Contato."""

    class Meta:
        model = Contact
        fields = [
            "kind",
            "value",
        ]


class ProfessionalSerializer(serializers.ModelSerializer[Professional]):
    """Serializador para o modelo de Profissional de Saúde (lista e escrita)."""

    social_name = serializers.CharField(max_length=255, required=True)
    profession = serializers.CharField(max_length=255, required=True)
    contacts = ContactSerializer(many=True, required=True)
    address = AddressSerializer(required=True, write_only=True)

    class Meta:
        model = Professional
        fields = [
            "uuid",
            "social_name",
            "profession",
            "address",
            "contacts",
        ]
        read_only_fields = ["uuid"]

    def create(self, validated_data: dict[str, Any]) -> Professional:
        """Delega criação para o service."""
        return ProfessionalService.create(validated_data)

    def update(
        self, instance: Professional, validated_data: dict[str, Any]
    ) -> Professional:
        """Delega atualização para o service."""
        return ProfessionalService.update(instance, validated_data)

    def to_representation(self, instance: Professional) -> dict[str, Any]:
        """Customiza a representação para retornar address como objeto único."""
        representation: dict[str, Any] = super().to_representation(instance)
        addresses = instance.addresses.all()
        representation["address"] = (
            AddressSerializer(addresses.first()).data if addresses.exists() else None
        )
        return representation


class ProfessionalDetailSerializer(ProfessionalSerializer):
    """Serializador para detalhes do Profissional (retrieve)."""

    class Meta(ProfessionalSerializer.Meta):
        fields = ProfessionalSerializer.Meta.fields + [
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]
