from rest_framework import serializers

from about.models import (
    Partner,
    Contact,
    New,
    NewGallery,
    Fillial
)


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'
        

class ConatactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        

class NewGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewGallery
        fields = ['image']
        

class NewsSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    watched_users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = New
        fields = '__all__'
    
    def get_gallery(self, instance):
        request = self.context.get('request')
        queryset = NewGallery.objects.filter(new=instance)
        images = [request.build_absolute_uri(obj.image.url) for obj in queryset]
        return images
    
    def get_watched_users_count(self, instance):
        return instance.watched_users.all().count()


class FillialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fillial
        fields = '__all__'
