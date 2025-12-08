from django.core.validators import RegexValidator
from django.db import models


class Address(models.Model):
    """Modelo de Endereço do Profissional."""

    zip_code_validator = RegexValidator(
        regex=r"^\d{8}$",
        message="CEP deve conter exatamente 8 dígitos numéricos.",
    )

    professional = models.ForeignKey(
        "Professional",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="Profissional",
    )
    street = models.CharField(
        max_length=255,
        verbose_name="Rua",
        help_text="Nome da rua/logradouro",
    )
    number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Número",
        help_text="Número do endereço",
    )
    neighborhood = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Bairro",
        help_text="Bairro",
    )
    complement = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Complemento",
        help_text="Complemento do endereço (ex: Apto 101, Bloco B)",
    )
    city = models.CharField(
        max_length=255,
        verbose_name="Cidade",
        help_text="Nome da cidade",
    )
    state = models.CharField(
        max_length=255,
        verbose_name="Estado",
        help_text="Nome ou sigla do estado",
    )
    zip_code = models.CharField(
        max_length=8,
        validators=[zip_code_validator],
        verbose_name="CEP",
        help_text="CEP com 8 dígitos (apenas números)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        ordering = ["street"]

    def __str__(self):
        return f"{self.street}, {self.number or 's/n'} - {self.city}/{self.state}"
