from django.urls import path

from flight.views import add_to_flight, add_to_box, my_view

urlpatterns = [
    path('', add_to_flight),
    path('add_to_box/', add_to_box),
    path('search/', my_view, name='my_view')
]
