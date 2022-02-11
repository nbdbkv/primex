from django.urls import path

from operation.views import (
    ParcelCreateView,
    ParcelOptionsListView,
    DeliveryStatusListView,
    DeliveryTypeListView,
    PackagingListView,
    PriceListView,
    PaymentTypeListView,
    PriceEnvelopListView,
    ParcelListView
)


urlpatterns = [
    path('create/', ParcelCreateView.as_view()),
    path('options/', ParcelOptionsListView.as_view()),
    path('delivery_statuses/', DeliveryStatusListView.as_view()),
    path('delivery_types/', DeliveryTypeListView.as_view()),
    path('packaging/', PackagingListView.as_view()),
    path('price_list/', PriceListView.as_view()),
    path('payment_types/', PaymentTypeListView.as_view()),
    path('envelops_prices/', PriceEnvelopListView.as_view()),
    path('parcel_list/', ParcelListView.as_view())
]
