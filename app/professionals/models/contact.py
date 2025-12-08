from django.db import models


class Contact(models.Model):
    """Modelo de Contato do Profissional."""

    class Kind(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        MOBILE = "mobile", "Celular"
        PHONE = "phone", "Telefone"
        EMAIL = "email", "E-mail"
        LINKEDIN = "linkedin", "LinkedIn"

    professional = models.ForeignKey(
        "professionals.Professional",
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Profissional",
        help_text="Profissional de saúde associado ao contato",
    )
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        verbose_name="Tipo",
        help_text="Tipo de contato (whatsapp, celular, telefone, e-mail, linkedin)",
    )
    value = models.CharField(
        max_length=255,
        verbose_name="Valor",
        help_text="Valor do contato (número, endereço de e-mail, URL, etc.)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ["kind"]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.value}"
