from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from account.validators import PhoneValidator
from about.models import Partner, Contact, New, NewGallery, Fillial, Question, Answer


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = "__all__"


class ConatactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class NewGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewGallery
        fields = ["image"]


class NewsSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = New
        fields = "__all__"

    def get_gallery(self, instance):
        request = self.context.get("request")
        queryset = NewGallery.objects.filter(new=instance)
        images = [request.build_absolute_uri(obj.image.url) for obj in queryset]
        return images

    def get_category(self, instance):
        return instance.category.name


class FillialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fillial
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = "__all__"

    def get_answer(self, instance):
        queryset = Answer.objects.filter(question=instance).values_list(
            "text", flat=True
        )
        return queryset


class FeedbackSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[PhoneValidator], max_length=15)
    name = serializers.CharField()
