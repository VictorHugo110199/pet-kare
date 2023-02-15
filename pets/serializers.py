from rest_framework import serializers
from .models import PetGender
from groups.serializers import  GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(choices = PetGender.choices, default=PetGender.DEFAULT)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)
     