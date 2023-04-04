from django.urls import path

from flight.views import add_to_flight, add_to_box

urlpatterns = [
    path('', add_to_flight),
    path('add_to_box/', add_to_box)
]
