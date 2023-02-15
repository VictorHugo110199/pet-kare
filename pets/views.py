from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView, Request, Response, status
from .models import *
from traits.models import Trait
from groups.models import Group
from django.shortcuts import get_object_or_404
from pet_kare.pagination import CustomPagination


class PetsView(APIView, CustomPagination):

    def get(self, request: Request):
        trait_name = request.query_params.get("trait", None)

        if trait_name is not None:
            trait_obj = Trait.objects.filter(name__iexact=trait_name).first()
            pet_list = Pet.objects.filter(traits=trait_obj)

            result_page = self.paginate_queryset(pet_list, request, view=self)

            serializer = PetSerializer(result_page, many=True)

            return self.get_paginated_response(serializer.data)

        pet_list = Pet.objects.all()
        result_page = self.paginate_queryset(pet_list, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)
        

    def post(self, request) -> Response:
        
        serializers = PetSerializer(data=request.data)
        
        serializers.is_valid(raise_exception=True)

        groups_data = serializers.validated_data.pop("group")

        def group_validete(group):

            group_exist = Group.objects.filter(
                scientific_name__iexact=group["scientific_name"]
            ).first()

            if not group_exist:
                group_exist = Group.objects.create(**group)

            return group_exist

        traits_data_list = serializers.validated_data.pop("traits")
       
        pet_obj = Pet.objects.create(**serializers.validated_data, group=group_validete(groups_data))

        for trait_data in traits_data_list:

            trait_obj = Trait.objects.filter(
                name__iexact=trait_data["name"]
            ).first()
            
            if not trait_obj:
                trait_obj = Trait.objects.create(**trait_data)

            pet_obj.traits.add(trait_obj)


        serializers = PetSerializer(pet_obj)
        
        return Response(serializers.data, status.HTTP_201_CREATED)

        
class PetIdView(APIView):

    def get(self, request: Request, pet_id: int) -> Response:

        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)

        return Response(serializer.data)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        groups_data = serializer.validated_data.pop("group", None)  

        if groups_data:
            group_name = groups_data["scientific_name"]
            group_obj = Group.objects.filter(scientific_name__iexact=group_name).first()
            if group_obj is None:
                group_obj = Group.objects.create(**groups_data)

            pet.group = group_obj

        traits_data_list = serializer.validated_data.pop("traits", None)

        if traits_data_list:
            traits = []
            for trait_dict in traits_data_list:
                trait_name = trait_dict["name"]
                trait = Trait.objects.filter(name__iexact=trait_name).first()

                if trait is None:
                    trait = Trait.objects.create(**trait_dict)

                traits.append(trait)

            pet.traits.set(traits)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data)


    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        pet.delete()

        return Response(status = status.HTTP_204_NO_CONTENT) 

