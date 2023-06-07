from django.contrib.sites.shortcuts import get_current_site

from rest_framework import serializers

from flight.models import Media, Rate, Contact, BaseParcel


class MediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('id', 'title', 'image', 'video',)

    def get_video(self, obj):
        url = 'http://' + f"{get_current_site(self.context['request'])}" + f'/flight/media/download/{obj.pk}/'
        return url


class RateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rate
        fields = ('weight', 'service_type', 'air', 'truck', 'commission',)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ('social', 'icon',)


class BaseParcelSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    flight_numeration = serializers.CharField(source='box.flight.numeration', default=None, read_only=True)

    class Meta:
        model = BaseParcel
        fields = (
            'created_at', 'arrived_at', 'track_code', 'client_code', 'phone', 'price', 'weight', 'cost', 'status',
            'status_label', 'flight_numeration',
        )
