import uuid

from django.db import models


class Appointment(models.Model):
    """Modelo de Consulta Médica."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    date = models.DateTimeField(
        verbose_name="Data da Consulta",
        help_text="Data e horário da consulta",
    )
    professional = models.ForeignKey(
        "professionals.Professional",
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Profissional",
        help_text="Profissional de saúde responsável pela consulta",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Consulta com {self.professional.social_name} em {self.date}"
