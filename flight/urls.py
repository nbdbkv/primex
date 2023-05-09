from django.urls import path

from flight.views import (
    add_to_flight, add_to_box, my_view, MediaListView, StatisticsListView, BaseParcelSearchListView, ContactListView,
)

urlpatterns = [
    path('', add_to_flight),
    path('add_to_box/', add_to_box),
    path('search/', my_view, name='my_view'),
    path("media/", MediaListView.as_view()),
    # path("stats/", StatisticsListView.as_view()),
    path("baseparcels/", BaseParcelSearchListView.as_view()),
    path("contact/", ContactListView.as_view()),
]
