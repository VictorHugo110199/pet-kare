from django.urls import path
from .views import PetsView
from .views import PetIdView


urlpatterns = [
    path("pets/", PetsView.as_view()),
    path("pets/<int:pet_id>/", PetIdView.as_view()),
]