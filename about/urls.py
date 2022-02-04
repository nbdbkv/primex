from django.urls import path

from about.views import (
    PartnerView,
    ContactView,
    NewsView,
    NewDetailView,
    FillialView
)


urlpatterns = [
    path('partners/', PartnerView.as_view()),
    path('contacts/', ContactView.as_view()),
    path('news/', NewsView.as_view()),
    path('new/<int:pk>/', NewDetailView.as_view()),
    path('fillials/', FillialView.as_view())
]

