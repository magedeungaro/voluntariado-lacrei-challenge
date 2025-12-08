from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from app.professionals.models import Address, Contact, Professional

User = get_user_model()


class ProfessionalAPITestCase(APITestCase):
    """Caso de teste base para testes da API de Profissionais."""

    def setUp(self):
        """Configura os dados de teste."""
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
        Contact.objects.create(
            professional=professional,
            kind="mobile",
            value="11988888888",
        )
        return professional


class TestProfessionalList(ProfessionalAPITestCase):
    """Testes para listagem de profissionais (GET /api/v1/professionals/)."""

    def test_list_professionals_returns_200(self):
        """Testa que o endpoint de listagem retorna 200 OK."""
        response = self.client.get("/api/v1/professionals/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_professionals_returns_empty_list(self):
        """Testa que a listagem retorna lista vazia quando não existem profissionais."""
        response = self.client.get("/api/v1/professionals/")
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])

    def test_list_professionals_returns_professionals(self):
        """Testa que a listagem retorna profissionais quando existem."""
        professional = self.create_professional()
        response = self.client.get("/api/v1/professionals/")
        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["uuid"], str(professional.uuid))
        self.assertEqual(data["results"][0]["social_name"], professional.social_name)
        self.assertEqual(data["results"][0]["profession"], professional.profession)

    def test_list_professionals_includes_address(self):
        """Testa que a listagem retorna profissionais com endereço."""
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
        """Testa que a listagem retorna profissionais com contatos."""
        self.create_professional()
        response = self.client.get("/api/v1/professionals/")
        data = response.json()

        contacts = data["results"][0]["contacts"]
        self.assertEqual(len(contacts), 2)
        kinds = [c["kind"] for c in contacts]
        self.assertIn("email", kinds)
        self.assertIn("mobile", kinds)


class TestProfessionalCreate(ProfessionalAPITestCase):
    """Testes para criação de profissionais (POST /api/v1/professionals/)."""

    def test_create_professional_returns_201(self):
        """Testa que o endpoint de criação retorna 201 Created."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_professional_returns_uuid(self):
        """Testa que a criação retorna o profissional com uuid."""
        response = self.client.post(
            "/api/v1/professionals/",
            data=self.professional_data,
            format="json",
        )
        data = response.json()

        self.assertIn("uuid", data)
        self.assertIsNotNone(data["uuid"])

    def test_create_professional_persists_data(self):
        """Testa que a criação persiste o profissional no banco de dados."""
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
        """Testa que a criação persiste o endereço."""
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
        """Testa que a criação persiste todos os contatos."""
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
    """Testes para obter detalhes de um profissional (GET /api/v1/professionals/{uuid}/)."""

    def test_retrieve_professional_returns_200(self):
        """Testa que o endpoint de detalhes retorna 200 OK."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_professional_returns_correct_data(self):
        """Testa que o endpoint retorna os dados corretos do profissional."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        self.assertEqual(data["uuid"], str(professional.uuid))
        self.assertEqual(data["social_name"], professional.social_name)
        self.assertEqual(data["profession"], professional.profession)

    def test_retrieve_professional_includes_timestamps(self):
        """Testa que o endpoint inclui created_at e updated_at."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIsNotNone(data["created_at"])
        self.assertIsNotNone(data["updated_at"])

    def test_retrieve_professional_includes_address(self):
        """Testa que o endpoint inclui o endereço."""
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
        """Testa que o endpoint inclui os contatos."""
        professional = self.create_professional()
        response = self.client.get(f"/api/v1/professionals/{professional.uuid}/")
        data = response.json()

        contacts = data["contacts"]
        self.assertEqual(len(contacts), 2)


class TestProfessionalUpdate(ProfessionalAPITestCase):
    """Testes para atualização de profissional (PUT /api/v1/professionals/{uuid}/)."""

    def test_update_professional_returns_200(self):
        """Testa que o endpoint de atualização retorna 200 OK."""
        professional = self.create_professional()
        response = self.client.put(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_professional_updates_basic_fields(self):
        """Testa que a atualização altera os campos básicos do profissional."""
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
        """Testa que a atualização altera o endereço do profissional."""
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
        """Testa que a atualização altera os contatos do profissional."""
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
        """Testa que a atualização retorna os dados atualizados do profissional."""
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
    """Testes para atualização parcial de profissional (PATCH /api/v1/professionals/{uuid}/)."""

    def test_partial_update_professional_returns_200(self):
        """Testa que o endpoint de atualização parcial retorna 200 OK."""
        professional = self.create_professional()
        response = self.client.patch(
            f"/api/v1/professionals/{professional.uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_professional_updates_fields(self):
        """Testa que a atualização parcial altera os campos especificados."""
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
    """Testes para exclusão de profissional (DELETE /api/v1/professionals/{uuid}/)."""

    def test_delete_professional_returns_204(self):
        """Testa que o endpoint de exclusão retorna 204 No Content."""
        professional = self.create_professional()
        response = self.client.delete(f"/api/v1/professionals/{professional.uuid}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_professional_removes_from_database(self):
        """Testa que a exclusão remove o profissional do banco de dados."""
        professional = self.create_professional()
        uuid = professional.uuid
        self.client.delete(f"/api/v1/professionals/{uuid}/")

        self.assertFalse(Professional.objects.filter(uuid=uuid).exists())

    def test_delete_professional_cascades_to_address(self):
        """Testa que a exclusão remove o endereço em cascata."""
        professional = self.create_professional()
        professional_id = professional.id
        self.client.delete(f"/api/v1/professionals/{professional.uuid}/")

        self.assertFalse(Address.objects.filter(professional_id=professional_id).exists())

    def test_delete_professional_cascades_to_contacts(self):
        """Testa que a exclusão remove os contatos em cascata."""
        professional = self.create_professional()
        professional_id = professional.id
        self.client.delete(f"/api/v1/professionals/{professional.uuid}/")

        self.assertFalse(Contact.objects.filter(professional_id=professional_id).exists())


class TestProfessionalErrors(ProfessionalAPITestCase):
    """Testes para tratamento de erros na API de Profissionais."""

    def test_create_professional_without_social_name_returns_400(self):
        """Testa que criar profissional sem social_name retorna 400."""
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
        """Testa que criar profissional sem profession retorna 400."""
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
        """Testa que criar profissional sem address retorna 400."""
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
        """Testa que criar profissional sem contacts retorna 400."""
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
        """Testa que criar profissional com lista de contatos vazia retorna 400."""
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
        """Testa que criar profissional com CEP inválido retorna 400."""
        data = self.professional_data.copy()
        data["address"]["zip_code"] = "123"  # Deveria ter 8 dígitos

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_professional_returns_404(self):
        """Testa que buscar profissional inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/v1/professionals/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_nonexistent_professional_returns_404(self):
        """Testa que atualizar profissional inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.put(
            f"/api/v1/professionals/{fake_uuid}/",
            data=self.professional_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_professional_returns_404(self):
        """Testa que excluir profissional inexistente retorna 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.delete(f"/api/v1/professionals/{fake_uuid}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_professional_with_invalid_contact_kind_returns_400(self):
        """Testa que criar profissional com tipo de contato inválido retorna 400."""
        data = self.professional_data.copy()
        data["contacts"] = [{"kind": "invalid_kind", "value": "test@test.com"}]

        response = self.client.post(
            "/api/v1/professionals/",
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_professional_with_invalid_uuid_returns_404(self):
        """Testa que buscar com formato de UUID inválido retorna 404."""
        response = self.client.get("/api/v1/professionals/invalid-uuid/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
