import uuid

from django.db import models


class Professional(models.Model):
    """Modelo de Profissional de Saúde."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    social_name = models.CharField(
        max_length=255,
        verbose_name="Nome Social",
        help_text="Nome social do profissional",
    )
    profession = models.CharField(
        max_length=255,
        verbose_name="Profissão",
        help_text="Ocupação profissional (ex: Médico, Enfermeiro, Psicólogo)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ["social_name"]

    def __str__(self):
        return f"{self.social_name} - {self.profession}"
