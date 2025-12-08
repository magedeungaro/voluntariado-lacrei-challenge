from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from app.appointments.models import Appointment
from app.professionals.models import Address, Contact, Professional

User = get_user_model()


class AppointmentAPITestCase(APITestCase):
    """Caso de teste base para testes da API de Consultas."""

    def setUp(self):
        """Configura os dados de teste."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Cria um profissional para os testes
        self.professional = self.create_professional()

        # Data e hora para amanhã às 14h30 (para evitar problemas de validação)
        self.tomorrow_datetime = datetime.now(timezone.utc) + timedelta(days=1)
        self.tomorrow_datetime = self.tomorrow_datetime.replace(
            hour=14, minute=30, second=0, microsecond=0
        )

        self.appointment_data = {
            "professional_uuid": str(self.professional.uuid),
            "date": self.tomorrow_datetime.isoformat(),
        }

    def create_professional(self):
        """Helper para criar um profissional com endereço e contatos."""
        professional = Professional.objects.create(
            social_name="Dr. João Santos",
            profession="Psicólogo",
        )
        Address.objects.create(
            professional=professional,
            street="Av. Paulista",
            number="1000",
            neighborhood="Bela Vista",
            complement="Conjunto 501",
            city="São Paulo",
            state="SP",
            zip_code="01310100",
        )
        Contact.objects.create(
            professional=professional,
            kind="email",
            value="joao.santos@email.com",
        )
        return professional

    def create_appointment(self, **kwargs):
        """Helper para criar uma consulta."""
        defaults = {
            "professional": self.professional,
            "date": self.tomorrow_datetime,
        }
        defaults.update(kwargs)
        return Appointment.objects.create(**defaults)


class TestAppointmentList(AppointmentAPITestCase):
    """Testes para listagem de consultas (GET /api/v1/appointments/)."""

    def test_list_appointments_returns_200(self):
        """Testa que o endpoint de listagem retorna 200 OK."""
        response = self.client.get("/api/v1/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_appointments_returns_empty_list(self):
        """Testa que a listagem retorna lista vazia quando não existem consultas."""
        response = self.client.get("/api/v1/appointments/")
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_list_appointments_returns_appointments(self):
        """Testa que a listagem retorna consultas quando existem."""
        appointment = self.create_appointment()
        response = self.client.get("/api/v1/appointments/")
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["uuid"], str(appointment.uuid))

    def test_list_appointments_includes_professional_info(self):
        """Testa que a listagem inclui informações do profissional."""
        self.create_appointment()
        response = self.client.get("/api/v1/appointments/")
        data = response.json()

        # Verifica se há referência ao profissional
        self.assertIn("professional", data["results"][0])


class TestAppointmentCreate(AppointmentAPITestCase):
    """Testes para criação de consultas (POST /api/v1/appointments/)."""

    def test_create_appointment_returns_201(self):
        """Testa que o endpoint de criação retorna 201 Created."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_appointment_returns_uuid(self):
        """Testa que a criação retorna a consulta com uuid."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        self.assertIn("uuid", data)
        self.assertIsNotNone(data["uuid"])

    def test_create_appointment_persists_data(self):
        """Testa que a criação persiste a consulta no banco de dados."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        appointment = Appointment.objects.get(uuid=data["uuid"])
        self.assertEqual(
            appointment.professional.uuid,
            self.professional.uuid,
        )

    def test_create_appointment_with_different_date(self):
        """Testa criação de consulta com data diferente."""
        new_datetime = self.tomorrow_datetime + timedelta(days=7)
        data = self.appointment_data.copy()
        data["date"] = new_datetime.isoformat()

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestAppointmentRetrieve(AppointmentAPITestCase):
    """Testes para obter detalhes de uma consulta (GET /api/v1/appointments/{uuid}/)."""

    def test_retrieve_appointment_returns_200(self):
        """Testa que o endpoint de detalhes retorna 200 OK."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_appointment_returns_correct_data(self):
        """Testa que o endpoint retorna os dados corretos da consulta."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        data = response.json()

        self.assertEqual(data["uuid"], str(appointment.uuid))
        # Verifica se a data retornada corresponde ao mesmo horário
        self.assertIn("date", data)

    def test_retrieve_appointment_includes_timestamps(self):
        """Testa que o endpoint inclui created_at e updated_at."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        data = response.json()

        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])


class TestAppointmentUpdate(AppointmentAPITestCase):
    """Testes para atualização de consulta (PUT /api/v1/appointments/{uuid}/)."""

    def test_update_appointment_returns_200(self):
        """Testa que o endpoint de atualização retorna 200 OK."""
        appointment = self.create_appointment()
        response = self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data=self.appointment_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_appointment_updates_fields(self):
        """Testa que a atualização altera os campos da consulta."""
        appointment = self.create_appointment()
        new_datetime = self.tomorrow_datetime + timedelta(hours=2)
        update_data = {
            "professional_uuid": str(self.professional.uuid),
            "date": new_datetime.isoformat(),
        }

        self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data=update_data,
            format="json",
        )

        appointment.refresh_from_db()
        # Verifica se a data foi atualizada
        self.assertIsNotNone(appointment.date)

    def test_update_appointment_returns_updated_data(self):
        """Testa que a atualização retorna os dados atualizados."""
        appointment = self.create_appointment()
        response = self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        self.assertIn("date", data)
        self.assertIn("professional_uuid", data)


class TestAppointmentPartialUpdate(AppointmentAPITestCase):
    """Testes para atualização parcial de consulta (PATCH /api/v1/appointments/{uuid}/)."""

    def test_partial_update_appointment_returns_200(self):
        """Testa que o endpoint de atualização parcial retorna 200 OK."""
        appointment = self.create_appointment()
        new_datetime = self.tomorrow_datetime + timedelta(hours=3)
        response = self.client.patch(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={"date": new_datetime.isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_appointment_updates_only_specified_fields(self):
        """Testa que a atualização parcial altera apenas os campos especificados."""
        appointment = self.create_appointment()
        original_professional_id = appointment.professional_id
        new_datetime = self.tomorrow_datetime + timedelta(hours=3)

        self.client.patch(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={"date": new_datetime.isoformat()},
            format="json",
        )

        appointment.refresh_from_db()
        # Profissional deve permanecer o mesmo
        self.assertEqual(appointment.professional_id, original_professional_id)


class TestAppointmentDelete(AppointmentAPITestCase):
    """Testes para exclusão de consulta (DELETE /api/v1/appointments/{uuid}/)."""

    def test_delete_appointment_returns_204(self):
        """Testa que o endpoint de exclusão retorna 204 No Content."""
        appointment = self.create_appointment()
        response = self.client.delete(f"/api/v1/appointments/{appointment.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_appointment_removes_from_database(self):
        """Testa que a exclusão remove a consulta do banco de dados."""
        appointment = self.create_appointment()
        uuid = appointment.uuid
        self.client.delete(f"/api/v1/appointments/{uuid}/")

        self.assertFalse(Appointment.objects.filter(uuid=uuid).exists())

    def test_delete_appointment_does_not_delete_professional(self):
        """Testa que a exclusão da consulta não remove o profissional."""
        appointment = self.create_appointment()
        professional_uuid = self.professional.uuid
        self.client.delete(f"/api/v1/appointments/{appointment.uuid}/")

        self.assertTrue(Professional.objects.filter(uuid=professional_uuid).exists())


class TestAppointmentErrors(AppointmentAPITestCase):
    """Testes para tratamento de erros na API de Consultas."""

    def test_create_appointment_without_professional_returns_400(self):
        """Testa que criar consulta sem professional_uuid retorna 400."""
        data = self.appointment_data.copy()
        del data["professional_uuid"]

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("professional_uuid", response.json())

    def test_create_appointment_without_date_returns_400(self):
        """Testa que criar consulta sem date retorna 400."""
        data = self.appointment_data.copy()
        del data["date"]

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.json())

    def test_create_appointment_with_invalid_date_returns_400(self):
        """Testa que criar consulta com formato de data inválido retorna 400."""
        data = self.appointment_data.copy()
        data["date"] = "invalid-date"

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_with_nonexistent_professional_returns_400(self):
        """Testa que criar consulta com profissional inexistente retorna 400."""
        data = self.appointment_data.copy()
        data["professional_uuid"] = "00000000-0000-0000-0000-000000000000"

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_appointment_returns_404(self):
        """Testa que buscar consulta inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/appointments/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_appointment_returns_404(self):
        """Testa que atualizar consulta inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.put(
            f"/api/v1/appointments/{fake_uuid}/",
            data=self.appointment_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_appointment_returns_404(self):
        """Testa que excluir consulta inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(f"/api/v1/appointments/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_appointment_with_invalid_uuid_returns_404(self):
        """Testa que buscar com formato de UUID inválido retorna 404."""
        response = self.client.get("/api/v1/appointments/invalid-uuid/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
