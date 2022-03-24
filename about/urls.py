from django.urls import path

from about.views import (
    PartnerView,
    ContactView,
    NewsView,
    NewDetailView,
    FillialView,
    QuestionView,
    FeedbackView,
)


urlpatterns = [
    path("partners/", PartnerView.as_view()),
    path("contacts/", ContactView.as_view()),
    path("articles/", NewsView.as_view()),
    path("article/<int:pk>/", NewDetailView.as_view()),
    path("branch_offices/", FillialView.as_view()),
    path("questions/", QuestionView.as_view()),
    path("feedback/", FeedbackView.as_view()),
]
