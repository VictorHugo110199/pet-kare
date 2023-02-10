from traits.models import Trait
from django.utils import timezone
from django.db import models
from django.test import TestCase
from unittest.mock import patch, MagicMock


class TraitModelTest(TestCase):
    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_field_created_at_properties(self, _: MagicMock):
        expected = timezone.now()
        trait_data = {"name": "trait"}
        created_trait = Trait.objects.create(**trait_data)

        received = created_trait.created_at
        message = "Verifique se o campo 'created_at' está sendo gerado exatamente no momento de criação da instância"

        self.assertEqual(received, expected, message)
