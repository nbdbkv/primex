from django.urls import path

from operation.views import (
    ParcelCreateView,
    DeliveryStatusListView,
    ParcelOptionsListView,
    DeliveryTypeListView,
    PackagingListView,
    EnvelopListView,
    PaymentTypeListView,
    GetUserBonusView,
    ParcelListView,
    ParcelRetrieveView

)


urlpatterns = [
    path('create/', ParcelCreateView.as_view()),
    path('options/', ParcelOptionsListView.as_view()),
    path('delivery_statuses/', DeliveryStatusListView.as_view()),
    path('delivery_types/', DeliveryTypeListView.as_view()),
    path('packaging/', PackagingListView.as_view()),
    path('envelops/', EnvelopListView.as_view()),
    path('payment_types/', PaymentTypeListView.as_view()),
    path('bonus/<int:pk>', GetUserBonusView.as_view()),
    path('parcel_list/', ParcelListView.as_view()),
    path('parcel/<int:pk>/', ParcelRetrieveView.as_view()),
]

