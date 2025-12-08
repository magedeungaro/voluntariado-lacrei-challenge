from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from app.professionals.models import Address, Contact, Professional

User = get_user_model()


class ProfessionalAPITestCase(APITestCase):
    """Base test case for Professional API tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        self.professional_data = {
            "social_name": "Dr. Maria Silva",
            "profession": "Médica",
            "address": {
                "street": "Rua das Flores",
                "number": "123",
                "neighborhood": "Centro",
                "complement": "Sala 101",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234567",
            },
            "contacts": [
                {"kind": "email", "value": "maria.silva@email.com"},
                {"kind": "whatsapp", "value": "11999999999"},
            ],
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
        Contact.objects.create(
            professional=professional,
            kind="mobile",
            value="11988888888",
        )
        return professional


class TestProfessionalList(ProfessionalAPITestCase):
    """Tests for listing professionals (GET /api/v1/professionals/)."""

    def test_list_professionals_returns_200(self):
        """Test that list endpoint returns 200 OK."""
        response = self.client.get("/api/v1/professionals/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_professionals_returns_empty_list(self):
        """Test that list returns empty list when no professionals exist."""
        response = self.client.get("/api/v1/professionals/")
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_list_professionals_returns_professionals(self):
        """Test that list returns professionals when they exist."""
        professional = self.create_professional()
        response = self.client.get("/api/v1/professionals/")
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["uuid"], str(professional.uuid))
        self.assertEqual(data["results"][0]["social_name"], professional.social_name)
        self.assertEqual(data["results"][0]["profession"], professional.profession)

    def test_list_professionals_includes_address(self):
        """Test that list returns professionals with address."""
        self.create_professional()
        response = self.client.get("/api/v1/professionals/")
        data = response.json()

        address = data["results"][0]["address"]
        self.assertEqual(address["street"], "Av. Paulista")
        self.assertEqual(address["number"], "1000")
        self.assertEqual(address["city"], "São Paulo")
        self.assertEqual(address["state"], "SP")
        self.assertEqual(address["zip_code"], "01310100")

    def test_list_professionals_includes_contacts(self):
        """Test that list returns professionals with contacts."""
        self.create_professional()
        response = self.client.get("/api/v1/professionals/")
        data = response.json()

        contacts = data["results"][0]["contacts"]
        self.assertEqual(len(contacts), 2)
        kinds = [c["kind"] for c in contacts]
        self.assertIn("email", kinds)
        self.assertIn("mobile", kinds)


class TestProfessionalCreate(ProfessionalAPITestCase):
    """Tests for creating professionals (POST /api/v1/professionals/)."""

    def test_create_professional_returns_201(self):
        """Test that create endpoint returns 201 Created."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_professional_returns_uuid(self):
        """Test that create returns the professional with uuid."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        self.assertIn("uuid", data)
        self.assertIsNotNone(data["uuid"])

    def test_create_professional_persists_data(self):
        """Test that create persists the professional in the database."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        professional = Professional.objects.get(uuid=data["uuid"])
        self.assertEqual(professional.social_name, self.professional_data["social_name"])
        self.assertEqual(professional.profession, self.professional_data["profession"])

    def test_create_professional_persists_address(self):
        """Test that create persists the address."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        professional = Professional.objects.get(uuid=data["uuid"])
        address = professional.addresses.first()

        self.assertEqual(address.street, self.professional_data["address"]["street"])
        self.assertEqual(address.number, self.professional_data["address"]["number"])
        self.assertEqual(address.city, self.professional_data["address"]["city"])
        self.assertEqual(address.state, self.professional_data["address"]["state"])
        self.assertEqual(address.zip_code, self.professional_data["address"]["zip_code"])

    def test_create_professional_persists_contacts(self):
        """Test that create persists all contacts."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        professional = Professional.objects.get(uuid=data["uuid"])
        contacts = professional.contacts.all()

        self.assertEqual(contacts.count(), 2)
        kinds = [c.kind for c in contacts]
        self.assertIn("email", kinds)
        self.assertIn("whatsapp", kinds)


class TestProfessionalRetrieve(ProfessionalAPITestCase):
    """Tests for retrieving a professional (GET /api/v1/professionals/{uuid}/)."""

    def test_retrieve_professional_returns_200(self):
        """Test that retrieve endpoint returns 200 OK."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_professional_returns_correct_data(self):
        """Test that retrieve returns the correct professional data."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        self.assertEqual(data["uuid"], str(professional.uuid))
        self.assertEqual(data["social_name"], professional.social_name)
        self.assertEqual(data["profession"], professional.profession)

    def test_retrieve_professional_includes_timestamps(self):
        """Test that retrieve includes created_at and updated_at."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_retrieve_professional_includes_address(self):
        """Test that retrieve includes address."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        address = data["address"]
        self.assertEqual(address["street"], "Av. Paulista")
        self.assertEqual(address["number"], "1000")
        self.assertEqual(address["neighborhood"], "Bela Vista")
        self.assertEqual(address["complement"], "Conjunto 501")
        self.assertEqual(address["city"], "São Paulo")
        self.assertEqual(address["state"], "SP")
        self.assertEqual(address["zip_code"], "01310100")

    def test_retrieve_professional_includes_contacts(self):
        """Test that retrieve includes contacts."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        contacts = data["contacts"]
        self.assertEqual(len(contacts), 2)


class TestProfessionalUpdate(ProfessionalAPITestCase):
    """Tests for updating a professional (PUT /api/v1/professionals/{uuid}/)."""

    def test_update_professional_returns_200(self):
        """Test that update endpoint returns 200 OK."""
        professional = self.create_professional()
        response = self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_professional_updates_basic_fields(self):
        """Test that update changes the professional's basic fields."""
        professional = self.create_professional()
        self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )

        professional.refresh_from_db()
        self.assertEqual(professional.social_name, self.professional_data["social_name"])
        self.assertEqual(professional.profession, self.professional_data["profession"])

    def test_update_professional_updates_address(self):
        """Test that update changes the professional's address."""
        professional = self.create_professional()
        self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )

        professional.refresh_from_db()
        address = professional.addresses.first()

        self.assertEqual(address.street, self.professional_data["address"]["street"])
        self.assertEqual(address.city, self.professional_data["address"]["city"])
        self.assertEqual(address.zip_code, self.professional_data["address"]["zip_code"])

    def test_update_professional_updates_contacts(self):
        """Test that update changes the professional's contacts."""
        professional = self.create_professional()
        self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )

        professional.refresh_from_db()
        contacts = professional.contacts.all()

        self.assertEqual(contacts.count(), 2)
        kinds = [c.kind for c in contacts]
        self.assertIn("email", kinds)
        self.assertIn("whatsapp", kinds)

    def test_update_professional_returns_updated_data(self):
        """Test that update returns the updated professional data."""
        professional = self.create_professional()
        response = self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        self.assertEqual(data["social_name"], self.professional_data["social_name"])
        self.assertEqual(data["profession"], self.professional_data["profession"])


class TestProfessionalPartialUpdate(ProfessionalAPITestCase):
    """Tests for partial update of a professional (PATCH /api/v1/professionals/{uuid}/)."""

    def test_partial_update_professional_returns_200(self):
        """Test that partial update endpoint returns 200 OK."""
        professional = self.create_professional()
        response = self.client.patch(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_professional_updates_fields(self):
        """Test that partial update changes the specified fields."""
        professional = self.create_professional()
        self.client.patch(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )

        professional.refresh_from_db()
        self.assertEqual(professional.social_name, self.professional_data["social_name"])
        self.assertEqual(professional.profession, self.professional_data["profession"])


class TestProfessionalDelete(ProfessionalAPITestCase):
    """Tests for deleting a professional (DELETE /api/v1/professionals/{uuid}/)."""

    def test_delete_professional_returns_204(self):
        """Test that delete endpoint returns 204 No Content."""
        professional = self.create_professional()
        response = self.client.delete(f"/api/v1/professionals/{professional.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_professional_removes_from_database(self):
        """Test that delete removes the professional from the database."""
        professional = self.create_professional()
        uuid = professional.uuid
        self.client.delete(f"/api/v1/professionals/{uuid}/")

        self.assertFalse(Professional.objects.filter(uuid=uuid).exists())

    def test_delete_professional_cascades_to_address(self):
        """Test that delete cascades to remove the address."""
        professional = self.create_professional()
        professional_id = professional.id
        self.client.delete(f"/api/v1/professionals/{professional.uuid}/")

        self.assertFalse(Address.objects.filter(professional_id=professional_id).exists())

    def test_delete_professional_cascades_to_contacts(self):
        """Test that delete cascades to remove the contacts."""
        professional = self.create_professional()
        professional_id = professional.id
        self.client.delete(f"/api/v1/professionals/{professional.uuid}/")

        self.assertFalse(Contact.objects.filter(professional_id=professional_id).exists())


class TestProfessionalErrors(ProfessionalAPITestCase):
    """Tests for error handling in Professional API."""

    def test_create_professional_without_social_name_returns_400(self):
        """Test that creating professional without social_name returns 400."""
        data = self.professional_data.copy()
        del data["social_name"]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("social_name", response.json())

    def test_create_professional_without_profession_returns_400(self):
        """Test that creating professional without profession returns 400."""
        data = self.professional_data.copy()
        del data["profession"]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profession", response.json())

    def test_create_professional_without_address_returns_400(self):
        """Test that creating professional without address returns 400."""
        data = self.professional_data.copy()
        del data["address"]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("address", response.json())

    def test_create_professional_without_contacts_returns_400(self):
        """Test that creating professional without contacts returns 400."""
        data = self.professional_data.copy()
        del data["contacts"]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contacts", response.json())

    def test_create_professional_with_empty_contacts_returns_400(self):
        """Test that creating professional with empty contacts list returns 400."""
        data = self.professional_data.copy()
        data["contacts"] = []

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("contacts", response.json())

    def test_create_professional_with_invalid_zip_code_returns_400(self):
        """Test that creating professional with invalid zip_code returns 400."""
        data = self.professional_data.copy()
        data["address"]["zip_code"] = "123"  # Should be 8 digits

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_professional_returns_404(self):
        """Test that retrieving non-existent professional returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/professionals/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_professional_returns_404(self):
        """Test that updating non-existent professional returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.put(
            f"/api/v1/professionals/{fake_uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_professional_returns_404(self):
        """Test that deleting non-existent professional returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(f"/api/v1/professionals/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_professional_with_invalid_contact_kind_returns_400(self):
        """Test that creating professional with invalid contact kind returns 400."""
        data = self.professional_data.copy()
        data["contacts"] = [{"kind": "invalid_kind", "value": "test@test.com"}]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_professional_with_invalid_uuid_returns_404(self):
        """Test that retrieving with invalid UUID format returns 404."""
        response = self.client.get("/api/v1/professionals/invalid-uuid/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
