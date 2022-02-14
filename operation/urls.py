from django.urls import path
from operation.views import (ParcelCreateView, GetParcelInfoView)


urlpatterns = [
    path('create/', ParcelCreateView.as_view()),
    path('get_parcel_info/<int:pk>', GetParcelInfoView.as_view()),
]

