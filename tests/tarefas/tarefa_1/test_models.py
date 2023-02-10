from django.test import TestCase
from pets.models import Pet
from groups.models import Group
from traits.models import Trait
from unittest.mock import patch, MagicMock
from django.utils import timezone
from django.db import models


class GroupModelTest(TestCase):
    def test_field_scientific_name_properties(self):
        expected = 50
        received = Group._meta.get_field("scientific_name").max_length
        message = "Verifique se o max_length do campo 'scientific_name' está com o valor correto."

        self.assertEqual(received, expected, message)

        expected = True
        received = Group._meta.get_field("scientific_name").unique
        message = "Verifique se o campo 'scientific_name' tem o atributo unique como verdadeiro."
        self.assertEqual(received, expected, message)

    @patch("django.utils.timezone.now", return_value="2022-11-27T17:55:22.819371Z")
    def test_field_created_at_properties(self, _: MagicMock):

        expected = timezone.now()
        group_data = {"scientific_name": "canis familiares"}
        created_group = Group.objects.create(**group_data)

        received = created_group.created_at
        message = "Verifique se o campo 'created_at' está sendo gerado exatamente no momento de criação da instância"

        self.assertEqual(received, expected, message)


class TraitModelTest(TestCase):
    def test_field_name_properties(self):
        expected = 20
        max_length = Trait._meta.get_field("name").max_length
        message = "Verifique se o max_length do campo 'name' está com o valor correto."

        self.assertEqual(max_length, expected, message)


class PetModelTest(TestCase):
    def test_field_name_properties(self):
        expected = 50
        max_length = Pet._meta.get_field("name").max_length
        message = "Verifique se o max_length do campo 'name' está com o valor correto."

        self.assertEqual(max_length, expected, message)

    def test_field_sex_properties(self):
        expected = 20
        max_length = Pet._meta.get_field("sex").max_length
        message = "Verifique se o max_length do campo 'sex' está com o valor correto."
        self.assertEqual(max_length, expected, message)
        # depende de como a pessoa setou na model: DEFAULT = 'Not Informed'
        # Algumas pessoas setam assim: NOT_INFORMED = 'Not Informed'
        expected = [("Male", "Male"), ("Female", "Female"), ("Not Informed", "Default")]
        choices = Pet._meta.get_field("sex").choices

        for expected_choice in expected:
            message = (
                f"Verifique se o campo 'sex' possui a choice '{expected_choice[0]}'"
            )
            self.assertIn(expected_choice, choices, message)

        expected = "Not Informed"
        default = getattr(Pet._meta.get_field("sex").default, "value", False)
        message = (
            "Verifique se o campo 'sex' possui valor padrão e se o valor está correto."
        )
        self.assertEqual(expected, default, message)


class PetGroupRelationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = Group.objects.create(scientific_name="Canis familiares")

        cls.pets = [
            Pet.objects.create(
                name=f"pet{i}", age=i, weight=12, sex="female", group=cls.group
            )
            for i in range(5)
        ]

    def test_if_a_group_can_have_many_pets(self):
        message = "Verifique se você setou corretamente o relacionamento 1:N entre Group e Pet."

        self.assertEqual(len(self.pets), self.group.pets.count(), message)

        for pet in self.pets:
            self.assertEqual(pet.group, self.group, message)

    def test_if_a_group_deletion_is_protected(self):
        message = "Verifique se você protegeu os pets de uma deleção de grupo associado a pets"

        with self.assertRaises(models.ProtectedError, msg=message):
            self.group.delete()


class PetTraitRelationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = Group.objects.create(scientific_name="Canis familiares")

        cls.pets = [
            Pet.objects.create(
                name=f"pet{i}", age=i, weight=12, sex="female", group=cls.group
            )
            for i in range(5)
        ]

        cls.traits = [Trait.objects.create(name=f"trait{i}") for i in range(5)]

    def test_if_trait_can_have_many_pets(self):
        message = "Verifique se você setou corretamente o relacionamento N:N entre Pet e Trait."

        for trait in self.traits:
            self.pets[0].traits.add(trait)

        self.assertEqual(len(self.traits), self.pets[0].traits.count(), message)
