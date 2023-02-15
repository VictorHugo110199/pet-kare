from unittest.mock import MagicMock, patch

from django.forms import model_to_dict
from rest_framework.test import APITestCase

from groups.models import Group
from pets.models import Pet
from traits.models import Trait
from tests.factories.pet_factories import create_multiple_pets


class PetDetailViewsTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.BASE_URL = "/api/pets/"

        cls.pet_data_1 = {
            "name": "strogonoff",
            "age": 2,
            "weight": 10.2,
            "sex": "female",
        }
        cls.pet_data_2 = {"name": "panqueca", "age": 2, "weight": 10.5}

        cls.group_data_1 = {"scientific_name": "canis familiaris"}
        cls.group_data_2 = {"scientific_name": "Felis catus"}

        cls.trait_data_1 = {"trait_name": "clever"}
        cls.trait_data_2 = {"trait_name": "friendly"}

        cls.pet_main_data = {
            "name": "Seraphim",
            "age": 1,
            "weight": 20,
            "sex": "Male",
            "group": cls.group_data_1,
            "traits": [cls.trait_data_1, cls.trait_data_2],
        }
        # cls.pet_main_data = {
        #     "name": "Minerva",
        #     "age": 6,
        #     "weight": 30.0,
        #     "sex": "Female",
        #     "group": {"scientific_name": "canis familiaris"},
        #     "traits": [
        #         {"name": "clever"},
        #         {"name": "friendly"},
        #         {"name": "playfull"},
        #     ],
        # }

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_can_list_pets_by_query_param(self, mock_now: MagicMock):
        group_data_1 = {"scientific_name": "canis familiaris"}
        trait_data_1 = {"name": "clever"}
        pets = create_multiple_pets(
            group_data=group_data_1,
            pet_count=1,
            traits_data=[trait_data_1],
        )
        pet1 = pets[0]

        group_data_2 = {"scientific_name": "canis lupus"}
        trait_data_2 = {"name": "friendly"}
        pets = create_multiple_pets(
            group_data=group_data_2,
            pet_count=3,
            traits_data=[trait_data_2],
        )

        QUERY_URL = self.BASE_URL + "?trait=clever"
        response = self.client.get(QUERY_URL, format="json")
        # ipdb.set_trace()

        # Status Code
        message = "\n Verifique se sua rota está retornando o status code 200."
        self.assertEqual(response.status_code, 200, message)

        message = "\n Verifique se as chaves corretas estão sendo retornadas na paginação da listagem de pets."
        self.assertIsInstance(
            response.json(),
            dict,
            "\n Verifique se o retorno da listagem de pets está retornando um dicionário corretamente",
        )
        expected_keys = {"count", "next", "previous", "results"}
        resulted_keys = set(response.json().keys())
        self.assertSetEqual(expected_keys, resulted_keys)

        # # Pets por page
        expected = 1
        message = "\n Verifique se sua rota está retornando apenas o(s) pet(s) com o trait buscado por query param"

        results = response.json()["results"]
        self.assertEqual(len(results), expected, message)

        group_dict = {**model_to_dict(pet1.group), "created_at": mock_now.return_value}
        trait1_dict = {
            **model_to_dict(pet1.traits.all()[0]),
            "created_at": mock_now.return_value,
        }
        trait1_dict.pop("pets", "")
        trait1_name = trait1_dict.pop("name")
        trait1_dict.update({"trait_name": trait1_name})
        # trait2_dict = {
        #     **model_to_dict(pet2.traits.all()[1]),
        #     "created_at": mock_now.return_value,
        # }
        # trait2_name = trait2_dict.pop("name")
        # trait2_dict.update({"trait_name": trait2_name})

        pet_dict_1 = {
            **model_to_dict(pet1),
            "traits": [trait1_dict],
            "group": group_dict,
        }

        pets = [pet_dict_1]

        message = "Verifique se sua rota está retornando todos os campos corretamente."

        self.assertListEqual(pets, results, message)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_can_retrieve_pet(self, mock_now: MagicMock):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        response = self.client.get(URL_DETAIL, format="json")

        message = "Verifique se sua rota de filtragem está funcionando corretamente."
        self.assertEqual(response.status_code, 200, message)

        message = "Verifique se sua rota de filtragem está funcionando corretamente."
        self.assertEqual(pet_1.id, response.json()["id"], message)

        message = "Verifique se sua rota está retornando todos os campos com a formatação correta."
        expected = {
            "id": 1,
            **self.pet_data_1,
            "group": {
                "id": 1,
                **self.group_data_1,
                "created_at": mock_now.return_value,
            },
            "traits": [],
        }
        self.assertEqual(expected, response.json(), message)

    def test_can_not_update_non_existing_pet_id(self):
        non_existing_id = 1312312
        URL_DETAIL = f"{self.BASE_URL}{non_existing_id}/"

        response = self.client.patch(URL_DETAIL, {}, format="json")

        message = "Verifique se sua rota de atualização está funcionando corretamente."
        self.assertEqual(response.status_code, 404, message)

        expected = {"detail": "Not found."}
        self.assertEqual(expected, response.json(), message)

    def test_can_update_pet_without_duplicating_existing_trait(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        trait_data_1 = {"name": "CLEVER"}

        trait = Trait.objects.create(**trait_data_1)
        pet_1.traits.add(trait)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        new_data = {"name": "Kazuki", "traits": [self.trait_data_1]}

        response = self.client.patch(URL_DETAIL, new_data, format="json")

        message = "Verifique se sua rota de atualização está funcionando corretamente."
        self.assertEqual(response.status_code, 200, message)
        self.assertEqual(new_data["name"], response.json()["name"], message)
        self.assertEqual(trait.id, response.json()["traits"][0]["id"], message)

    def test_can_update_pet_without_duplicating_existing_group(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        new_data = {"name": "Kazuki", "group": self.group_data_1}

        response = self.client.patch(URL_DETAIL, new_data, format="json")

        message = "Verifique se sua rota de atualização está funcionando corretamente."
        self.assertEqual(response.status_code, 200, message)
        self.assertEqual(new_data["name"], response.json()["name"], message)
        self.assertEqual(group.id, response.json()["group"]["id"], message)

    def test_can_update_pet_traits(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        trait_data_1 = {"name": "CLEVER"}
        trait_data_2 = {"trait_name": "friendly"}
        trait = Trait.objects.create(**trait_data_1)
        pet_1.traits.add(trait)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        new_data = {"traits": [trait_data_2]}
        response = self.client.patch(URL_DETAIL, new_data, format="json")

        message = "Verifique se sua rota de atualização está retornando o status code correto."
        self.assertEqual(response.status_code, 200, message)

        message = "Verifique se sua rota de atualização está substituindo todas as traits antigas e deixando somente as novas"
        self.assertEqual(
            pet_1.traits.first().id, response.json()["traits"][0]["id"], message
        )

    def test_can_update_pet_group(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        new_data = {"group": self.group_data_2}
        response = self.client.patch(URL_DETAIL, new_data, format="json")

        message = "Verifique se sua rota de atualização está retornando o status code correto."
        self.assertEqual(response.status_code, 200, message)

        message = "Verifique se sua rota de atualização está substituindo o grupo anterior pelo novo."
        self.assertEqual(2, response.json()["group"]["id"], message)

    def test_can_not_update_pet_with_invalid_sex_field(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        new_data = {"sex": "oi"}
        response = self.client.patch(URL_DETAIL, new_data, format="json")

        message = "Verifique se sua rota de atualização está retornando o status code correto."
        self.assertEqual(response.status_code, 400, message)

        message = "Verifique se sua rota de atualização está substituindo o grupo anterior pelo novo."
        expected = {"sex": ['"oi" is not a valid choice.']}
        self.assertEqual(expected, response.json(), message)

    def test_can_not_delete_non_existing_pet_id(self):
        id_does_not_exists = 1312312
        URL_DETAIL = f"{self.BASE_URL}{id_does_not_exists}/"

        response = self.client.delete(URL_DETAIL)
        message = (
            "Verifique se seua rota de deleção está retornando o status code correto"
        )
        self.assertEqual(response.status_code, 404, message)

    def test_can_delete_pet(self):
        group = Group.objects.create(**self.group_data_1)
        pet_1 = Pet.objects.create(**self.pet_data_1, group=group)

        URL_DETAIL = f"{self.BASE_URL}{pet_1.id}/"
        response = self.client.delete(URL_DETAIL)
        message = (
            "Verifique se sua rota de deleção está retornando o status code correto."
        )
        self.assertEqual(response.status_code, 204, message)

        message = "Verifique se sua rota de deleção está excluindo corretamente o pet do banco de dados."
        self.assertEqual(0, Pet.objects.all().count(), message)
