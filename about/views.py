from rest_framework import generics
from rest_framework.response import Response

from about.models import Partner, Contact, New, Fillial, Question
from about.utils import send_email
from about.serializers import (
    PartnerSerializer,
    ConatactSerializer,
    NewsSerializer,
    FillialSerializer,
    QuestionSerializer,
    FeedbackSerializer,
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

    def get_object(self):
        article = super().get_object()
        article.watched_count += 1
        article.save()
        return article


class FillialView(generics.ListAPIView):
    queryset = Fillial.objects.all()
    serializer_class = FillialSerializer


class QuestionView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class FeedbackView(generics.GenericAPIView):
    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.data).data
        text = f'Name: {serializer.get("name")}\n' f'Phone: {serializer.get("phone")}'
        send_email(text)
        return Response()
