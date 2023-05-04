from rest_framework import serializers

from flight.models import Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ('title', 'media',)
