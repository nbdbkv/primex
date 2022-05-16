from django.urls import path

from operation.views import (
    ParcelCreateView,
    DeliveryStatusListView,
    ParcelOptionsListView,
    DeliveryTypeListView,
    PackagingListView,
    EnvelopListView,
    PaymentHistoryView,
    PaymentTypeListView,
    ParcelListView,
    ParcelRetrieveView,
    BonusHistoryView,
    PrintView,
    ParcelImageCreateView
)


urlpatterns = [
    path("create/", ParcelCreateView.as_view()),
    path("options/", ParcelOptionsListView.as_view()),
    path("delivery_statuses/", DeliveryStatusListView.as_view()),
    path("delivery_types/", DeliveryTypeListView.as_view()),
    path("packaging/", PackagingListView.as_view()),
    path("envelops/", EnvelopListView.as_view()),
    path("payment_types/", PaymentTypeListView.as_view()),
    path("parcel_list/", ParcelListView.as_view()),
    path("parcel/<str:code>/", ParcelRetrieveView.as_view()),
    path("payment_history/", PaymentHistoryView.as_view()),
    path("bonus/", BonusHistoryView.as_view()),
    path("print/<int:pk>/", PrintView.as_view(), name="print"),
    path("image/", ParcelImageCreateView.as_view())
]
