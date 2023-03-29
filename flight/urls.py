from django.urls import path

from flight.views import add_to_flight

urlpatterns = [
    path('', add_to_flight)
]
