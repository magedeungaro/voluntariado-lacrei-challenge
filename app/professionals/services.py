from rest_framework.exceptions import ValidationError

from .models import Address, Contact, Professional


class ProfessionalService:
    """Service layer para operações de Profissional."""

    @staticmethod
    def validate(data):
        """Valida dados do profissional."""
        errors = {}

        if not data.get("social_name"):
            errors["social_name"] = ["Nome social é obrigatório."]

        if not data.get("profession"):
            errors["profession"] = ["Profissão é obrigatória."]

        if not data.get("address"):
            errors["address"] = ["Endereço é obrigatório."]

        contacts = data.get("contacts")
        if not contacts or len(contacts) == 0:
            errors["contacts"] = ["Pelo menos um contato é obrigatório."]

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def create(validated_data):
        """Cria profissional com endereço e contatos."""
        ProfessionalService.validate(validated_data)

        address_data = validated_data.pop("address")
        contacts_data = validated_data.pop("contacts")

        professional = Professional.objects.create(**validated_data)

        Address.objects.create(professional=professional, **address_data)

        for contact_data in contacts_data:
            Contact.objects.create(professional=professional, **contact_data)

        return professional

    @staticmethod
    def update(instance, validated_data):
        """Atualiza profissional com endereço e contatos."""
        ProfessionalService.validate(validated_data)

        address_data = validated_data.pop("address")
        contacts_data = validated_data.pop("contacts")

        # Atualiza campos do profissional
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualiza endereço
        instance.addresses.all().delete()
        Address.objects.create(professional=instance, **address_data)

        # Atualiza contatos
        instance.contacts.all().delete()
        for contact_data in contacts_data:
            Contact.objects.create(professional=instance, **contact_data)

        return instance
