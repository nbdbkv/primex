from rest_framework import generics

from about.models import (
    Partner,
    Contact,
    New,
    Fillial,
    Question
)
from about.serializers import (
    PartnerSerializer,
    ConatactSerializer,
    NewsSerializer,
    FillialSerializer,
    QuestionSerializer
)


class PartnerView(generics.ListAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class ContactView(generics.ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ConatactSerializer


class NewsView(generics.ListAPIView):
    queryset = New.objects.all()
    serializer_class = NewsSerializer


class NewDetailView(generics.RetrieveAPIView):
    queryset = New.objects.all()
    serializer_class = NewsSerializer


class FillialView(generics.ListAPIView):
    queryset = Fillial.objects.all()
    serializer_class = FillialSerializer


class QuestionView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
