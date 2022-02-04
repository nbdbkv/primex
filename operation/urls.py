from django.urls import path, include

from .views import (CreateParcelView, UpdateParcelView, ListParcelView, PaymentParcelView, PaymentParcelWithBonusView)

urlpatterns = [
    path('create/', CreateParcelView.as_view()),
    path('update/<int:pk>', UpdateParcelView.as_view()),
    path('list/', ListParcelView.as_view()),
    path('payment/<int:pk>', PaymentParcelView.as_view()),
    path('bonus/<int:pk>', PaymentParcelWithBonusView.as_view())
]