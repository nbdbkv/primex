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
        fields = '__all__'
        

class NewsSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    watched_users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = New
        fields = ['title', 'description', 'border_photo', 'watched_users_count', 'create_at', 'gallery']
    
    def get_gallery(self, instance):
        queryset = NewGallery.objects.filter(new=instance)
        serializer = NewGallerySerializer(queryset, many=True)
        return serializer.data
    
    def get_watched_users_count(self, instance):
        return instance.watched_users.all().count()


class FillialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fillial
        fields = '__all__'
