from django.urls import path
from operation.views import ParcelCreateView


urlpatterns = [
    path('create/', ParcelCreateView.as_view()),
]

