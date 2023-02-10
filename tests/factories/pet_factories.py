from groups.models import Group
from pets.models import Pet
from django.db.models import QuerySet
from traits.models import Trait


def create_multiple_pets(
    group_data: dict, pet_count: int, traits_data: list | None = None
) -> QuerySet[Pet]:

    pets_data = [
        {
            "name": f"strogonoff {index}",
            "age": 2,
            "weight": 10.2,
            "sex": "female",
        }
        for index in range(0, pet_count)
    ]

    group_obj = Group.objects.create(**group_data)

    pets_objects = [Pet.objects.create(**pet_dict, group=group_obj) for pet_dict in pets_data]

    if traits_data:
        for trait_dict in traits_data:
            trait = Trait.objects.create(**trait_dict)
            for pet in pets_objects:
                pet.traits.add(trait)
    return pets_objects
