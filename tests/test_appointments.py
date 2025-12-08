from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from app.appointments.models import Appointment
from app.professionals.models import Address, Contact, Professional

User = get_user_model()


class AppointmentAPITestCase(APITestCase):
    """Base test case for Appointment API tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        # Create a professional for appointments
        self.professional = self.create_professional()

        # Appointment data for creating appointments
        self.appointment_data = {
            "date": (timezone.now() + timedelta(days=7)).isoformat(),
            "professional_uuid": str(self.professional.uuid),
        }

    def create_professional(self):
        """Helper to create a professional with address and contacts."""
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

    def create_appointment(self, professional=None, date=None):
        """Helper to create an appointment."""
        if professional is None:
            professional = self.professional
        if date is None:
            date = timezone.now() + timedelta(days=7)

        return Appointment.objects.create(
            professional=professional,
            date=date,
        )


class TestAppointmentList(AppointmentAPITestCase):
    """Tests for listing appointments (GET /api/v1/appointments/)."""

    def test_list_appointments_returns_200(self):
        """Test that list endpoint returns 200 OK."""
        response = self.client.get("/api/v1/appointments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_appointments_returns_empty_list(self):
        """Test that list returns empty list when no appointments exist."""
        response = self.client.get("/api/v1/appointments/")
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_list_appointments_returns_appointments(self):
        """Test that list returns appointments when they exist."""
        appointment = self.create_appointment()
        response = self.client.get("/api/v1/appointments/")
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["uuid"], str(appointment.uuid))

    def test_list_appointments_includes_professional_data(self):
        """Test that list returns appointments with professional data."""
        self.create_appointment()
        response = self.client.get("/api/v1/appointments/")
        data = response.json()

        professional = data["results"][0]["professional"]
        self.assertEqual(professional["uuid"], str(self.professional.uuid))
        self.assertEqual(professional["social_name"], self.professional.social_name)
        self.assertEqual(professional["profession"], self.professional.profession)

    def test_list_appointments_filter_by_professional_uuid(self):
        """Test that list can filter by professional_uuid."""
        # Create another professional
        other_professional = Professional.objects.create(
            social_name="Dr. Maria Silva",
            profession="Médica",
        )
        Address.objects.create(
            professional=other_professional,
            street="Rua das Flores",
            number="200",
            city="São Paulo",
            state="SP",
            zip_code="01234567",
        )
        Contact.objects.create(
            professional=other_professional,
            kind="email",
            value="maria@email.com",
        )

        # Create appointments for both professionals
        self.create_appointment(professional=self.professional)
        self.create_appointment(professional=other_professional)

        # Filter by professional_uuid
        response = self.client.get(
            f"/api/v1/appointments/?professional_uuid={self.professional.uuid}"
        )
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["professional"]["uuid"], str(self.professional.uuid)
        )


class TestAppointmentCreate(AppointmentAPITestCase):
    """Tests for creating appointments (POST /api/v1/appointments/)."""

    def test_create_appointment_returns_201(self):
        """Test that create endpoint returns 201 Created."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_appointment_returns_uuid(self):
        """Test that create returns the appointment with uuid."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        self.assertIn("uuid", data)
        self.assertIsNotNone(data["uuid"])

    def test_create_appointment_persists_data(self):
        """Test that create persists the appointment in the database."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        appointment = Appointment.objects.get(uuid=data["uuid"])
        self.assertEqual(appointment.professional.uuid, self.professional.uuid)

    def test_create_appointment_links_to_professional(self):
        """Test that create correctly links appointment to professional."""
        response = self.client.post(
            "/api/v1/appointments/",
            data=self.appointment_data,
            format="json",
        )
        data = response.json()

        appointment = Appointment.objects.get(uuid=data["uuid"])
        self.assertEqual(appointment.professional, self.professional)


class TestAppointmentRetrieve(AppointmentAPITestCase):
    """Tests for retrieving an appointment (GET /api/v1/appointments/{uuid}/)."""

    def test_retrieve_appointment_returns_200(self):
        """Test that retrieve endpoint returns 200 OK."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_appointment_returns_correct_data(self):
        """Test that retrieve returns the correct appointment data."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        data = response.json()

        self.assertEqual(data["uuid"], str(appointment.uuid))

    def test_retrieve_appointment_includes_timestamps(self):
        """Test that retrieve includes created_at and updated_at."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        data = response.json()

        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_retrieve_appointment_includes_professional(self):
        """Test that retrieve includes professional details."""
        appointment = self.create_appointment()
        response = self.client.get(f"/api/v1/appointments/{appointment.uuid}/")
        data = response.json()

        professional = data["professional"]
        self.assertEqual(professional["uuid"], str(self.professional.uuid))
        self.assertEqual(professional["social_name"], self.professional.social_name)
        self.assertEqual(professional["profession"], self.professional.profession)


class TestAppointmentUpdate(AppointmentAPITestCase):
    """Tests for updating an appointment (PUT /api/v1/appointments/{uuid}/)."""

    def test_update_appointment_returns_200(self):
        """Test that update endpoint returns 200 OK."""
        appointment = self.create_appointment()
        new_date = (timezone.now() + timedelta(days=14)).isoformat()

        response = self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={
                "date": new_date,
                "professional_uuid": str(self.professional.uuid),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_appointment_updates_date(self):
        """Test that update changes the appointment's date."""
        appointment = self.create_appointment()
        new_date = timezone.now() + timedelta(days=14)

        self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={
                "date": new_date.isoformat(),
                "professional_uuid": str(self.professional.uuid),
            },
            format="json",
        )

        appointment.refresh_from_db()
        # Compare dates ignoring microseconds
        self.assertEqual(
            appointment.date.replace(microsecond=0),
            new_date.replace(microsecond=0),
        )

    def test_update_appointment_changes_professional(self):
        """Test that update can change the professional."""
        appointment = self.create_appointment()

        # Create another professional
        other_professional = Professional.objects.create(
            social_name="Dr. Maria Silva",
            profession="Médica",
        )
        Address.objects.create(
            professional=other_professional,
            street="Rua das Flores",
            number="200",
            city="São Paulo",
            state="SP",
            zip_code="01234567",
        )
        Contact.objects.create(
            professional=other_professional,
            kind="email",
            value="maria@email.com",
        )

        self.client.put(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={
                "date": self.appointment_data["date"],
                "professional_uuid": str(other_professional.uuid),
            },
            format="json",
        )

        appointment.refresh_from_db()
        self.assertEqual(appointment.professional, other_professional)


class TestAppointmentPartialUpdate(AppointmentAPITestCase):
    """Tests for partial update of an appointment (PATCH /api/v1/appointments/{uuid}/)."""

    def test_partial_update_appointment_returns_200(self):
        """Test that partial update endpoint returns 200 OK."""
        appointment = self.create_appointment()
        new_date = (timezone.now() + timedelta(days=14)).isoformat()

        response = self.client.patch(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={"date": new_date},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_appointment_updates_date(self):
        """Test that partial update changes the date."""
        appointment = self.create_appointment()
        new_date = timezone.now() + timedelta(days=14)

        self.client.patch(
            f"/api/v1/appointments/{appointment.uuid}/",
            data={"date": new_date.isoformat()},
            format="json",
        )

        appointment.refresh_from_db()
        self.assertEqual(
            appointment.date.replace(microsecond=0),
            new_date.replace(microsecond=0),
        )


class TestAppointmentDelete(AppointmentAPITestCase):
    """Tests for deleting an appointment (DELETE /api/v1/appointments/{uuid}/)."""

    def test_delete_appointment_returns_204(self):
        """Test that delete endpoint returns 204 No Content."""
        appointment = self.create_appointment()
        response = self.client.delete(f"/api/v1/appointments/{appointment.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_appointment_removes_from_database(self):
        """Test that delete removes the appointment from the database."""
        appointment = self.create_appointment()
        uuid = appointment.uuid
        self.client.delete(f"/api/v1/appointments/{uuid}/")

        self.assertFalse(Appointment.objects.filter(uuid=uuid).exists())

    def test_delete_appointment_does_not_delete_professional(self):
        """Test that deleting appointment does not delete the professional."""
        appointment = self.create_appointment()
        professional_uuid = self.professional.uuid

        self.client.delete(f"/api/v1/appointments/{appointment.uuid}/")

        self.assertTrue(Professional.objects.filter(uuid=professional_uuid).exists())


class TestAppointmentErrors(AppointmentAPITestCase):
    """Tests for error handling in Appointment API."""

    def test_create_appointment_without_date_returns_400(self):
        """Test that creating appointment without date returns 400."""
        data = {"professional_uuid": str(self.professional.uuid)}

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.json())

    def test_create_appointment_without_professional_returns_400(self):
        """Test that creating appointment without professional returns 400."""
        data = {"date": (timezone.now() + timedelta(days=7)).isoformat()}

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("professional_uuid", response.json())

    def test_create_appointment_with_invalid_professional_returns_400(self):
        """Test that creating appointment with non-existent professional returns 400."""
        data = {
            "date": (timezone.now() + timedelta(days=7)).isoformat(),
            "professional_uuid": "00000000-0000-0000-0000-000000000000",
        }

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_with_invalid_date_format_returns_400(self):
        """Test that creating appointment with invalid date format returns 400."""
        data = {
            "date": "invalid-date",
            "professional_uuid": str(self.professional.uuid),
        }

        response = self.client.post(
            "/api/v1/appointments/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.json())

    def test_retrieve_nonexistent_appointment_returns_404(self):
        """Test that retrieving non-existent appointment returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/appointments/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_appointment_returns_404(self):
        """Test that updating non-existent appointment returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.put(
            f"/api/v1/appointments/{fake_uuid}/",
            data=self.appointment_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_appointment_returns_404(self):
        """Test that deleting non-existent appointment returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(f"/api/v1/appointments/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_appointment_with_invalid_uuid_returns_404(self):
        """Test that retrieving with invalid UUID format returns 404."""
        response = self.client.get("/api/v1/appointments/invalid-uuid/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_appointment_with_empty_body_returns_400(self):
        """Test that creating appointment with empty body returns 400."""
        response = self.client.post(
            "/api/v1/appointments/",
            data={},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_invalid_professional_uuid_returns_empty(self):
        """Test that filtering by non-existent professional returns empty list."""
        self.create_appointment()
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        response = self.client.get(f"/api/v1/appointments/?professional_uuid={fake_uuid}")
        data = response.json()

        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])
