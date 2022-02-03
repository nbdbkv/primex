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
    path('articles/', NewsView.as_view()),
    path('article/<int:pk>/', NewDetailView.as_view()),
    path('branch_offices/', FillialView.as_view())
]

