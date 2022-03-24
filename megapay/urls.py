import os
from django.urls import path

from megapay.views import ( CreateOrder
                            ,)

urlpatterns = [
    path('orders/', CreateOrder.as_view()),
]
