from unittest.mock import MagicMock, patch

from django.forms import model_to_dict
from rest_framework.test import APITestCase

from groups.models import Group
from pets.models import Pet
from traits.models import Trait
from tests.factories.pet_factories import create_multiple_pets


class PetViewsTest(APITestCase):
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
    def test_can_list_pets_with_pagination(self, mock_now: MagicMock):
        group_data_1 = {"scientific_name": "canis familiaris"}
        trait_data_1 = {"name": "clever"}
        trait_data_2 = {"name": "friendly"}
        pets = create_multiple_pets(
            group_data=group_data_1,
            pet_count=5,
            traits_data=[trait_data_1, trait_data_2],
        )
        pet1, pet2, *_ = pets
        response = self.client.get(self.BASE_URL, format="json")

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

        # Pets por page
        expected = 2
        message = "\n Verifique se sua rota está retornando apenas 2 pets por página"

        results = response.json()["results"]
        for r in results:
            r.pop('pets', '')
        self.assertEqual(len(results), expected, message)

        group_dict = {**model_to_dict(pet1.group), "created_at": mock_now.return_value}
        trait1_dict = {
            **model_to_dict(pet2.traits.all()[0]),
            "created_at": mock_now.return_value,
        }
        trait1_name = trait1_dict.pop("name")
        trait1_dict.update({"trait_name": trait1_name})
        trait2_dict = {
            **model_to_dict(pet2.traits.all()[1]),
            "created_at": mock_now.return_value,
        }
        trait2_name = trait2_dict.pop("name")
        trait2_dict.update({"trait_name": trait2_name})

        pet_dict_1 = {
            **model_to_dict(pet1),
            "traits": [trait1_dict, trait2_dict],
            "group": group_dict,
        }

        pet_dict_2 = {
            **model_to_dict(pet2),
            "traits": [trait1_dict, trait2_dict],
            "group": group_dict,
        }
        [a.pop('pets','') for a in pet_dict_1["traits"]]
        [a.pop('pets','') for a in pet_dict_2["traits"]]
        pets = [pet_dict_1, pet_dict_2]

        message = "Verifique se sua rota está retornando todos os campos corretamente."

        for pet in pets:
            self.assertIn(pet, results, message)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_can_create_pet(self, mock_now: MagicMock):
        response = self.client.post(
            self.BASE_URL,
            self.pet_main_data,
            format="json",
        )
        message = "Verifique se sua rota está retornando o status code 201."
        self.assertEqual(response.status_code, 201, message)

        expected = {
            "id": 1,
            "name": "Seraphim",
            "age": 1,
            "weight": 20.0,
            "sex": "Male",
            "group": {
                "id": 1,
                **self.group_data_1,
                "created_at": mock_now.return_value,
            },
            "traits": [
                {"id": 1, **self.trait_data_1, "created_at": mock_now.return_value},
                {"id": 2, **self.trait_data_2, "created_at": mock_now.return_value},
            ],
        }
        message = "Verifique se sua rota está retornando todos os campos com a formatação correta."
        self.assertEqual(expected, response.json(), message)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_can_create_pet_without_duplicating_a_group_already_exists(
        self, mock_now: MagicMock
    ):
        group = Group.objects.create(**self.group_data_1)

        response = self.client.post(
            self.BASE_URL,
            self.pet_main_data,
            format="json",
        )

        message = "\n Verifique se sua rota está retornando o status code 201."
        self.assertEqual(response.status_code, 201, message)

        message = "\n Verifique se você está reutilizando o grupo que já existe no banco de dados ao invés de criar um novo."
        self.assertEqual(group.id, response.json()["group"]["id"], message)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_can_create_pet_without_duplicating_a_trait_that_already_exists(
        self, mock_now: MagicMock
    ):
        trait_data_1 = {"name": "CLEVER"}
        trait_data_2 = {"name": "FRIENDLY"}
        trait1 = Trait.objects.create(**trait_data_1)
        trait2 = Trait.objects.create(**trait_data_2)
        response = self.client.post(
            self.BASE_URL,
            self.pet_main_data,
            format="json",
        )

        message = "Verifique se sua rota está retornando o status code 201."
        self.assertEqual(response.status_code, 201, message)

        message = "Verifique se você está reutilizando o trait que já existe no banco de dados ao invés de criar um novo."
        self.assertEqual(trait1.id, response.json()["traits"][0]["id"], message)

        message = "Verifique se um novo trait está sendo criado quando necessário"
        self.assertEqual(trait2.id, response.json()["traits"][1]["id"], message)

    def test_can_not_create_pet_when_missing_keys(self):

        response = self.client.post(
            self.BASE_URL,
            {},
            format="json",
        )

        message = "Verifique se sua rota está retornando o status code 400."
        self.assertEqual(response.status_code, 400, message)

        expected = {
            "name": ["This field is required."],
            "age": ["This field is required."],
            "weight": ["This field is required."],
            "group": ["This field is required."],
            "traits": ["This field is required."],
        }
        message = "Verifique se você colocou como obrigatório todos os campos que são pedidos na entrega."
        self.assertEqual(expected, response.json(), message)
