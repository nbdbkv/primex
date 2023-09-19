from django.urls import path

from flight.views import (
    add_to_flight, add_to_box, my_view, delivery_view, MediaListView, FileDownloadListView, RateListView,
    ContactListView, BaseParcelSearchListView, BaseParcelHistoryListView, ajax_get_track_code_view,
    OrderDescriptionListView, BaseParcelCreateView, ajax_get_phone_view, ajax_get_client_code_view
)

urlpatterns = [
    path('', add_to_flight),
    path('add_to_box/', add_to_box),
    path('arrival/search/', my_view, name='my_view'),
    path('delivery/search/', delivery_view, name='delivery_view'),
    path("media/", MediaListView.as_view()),
    path('media/download/<int:id>/', FileDownloadListView.as_view()),
    path("rate/", RateListView.as_view()),
    path("order_description/", OrderDescriptionListView.as_view()),
    path("contact/", ContactListView.as_view()),
    path("baseparcels/", BaseParcelSearchListView.as_view()),
    path("history/", BaseParcelHistoryListView.as_view()),
    path('track_code/', ajax_get_track_code_view, name='track_code'),
    path("create_baseparcel/", BaseParcelCreateView.as_view()),
    path('phone/', ajax_get_phone_view, name='phone'),
    path('client_code/', ajax_get_client_code_view, name='phone'),
]
