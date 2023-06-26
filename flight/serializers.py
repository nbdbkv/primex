from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from flight.models import BaseParcel, Contact, Media, OrderDescription, Rate


class MediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('id', 'title', 'icon', 'image', 'video',)

    def get_video(self, obj):
        if obj.video:
            url = 'http://' + f"{get_current_site(self.context['request'])}" + f'/flight/media/download/{obj.pk}/'
            return url
        else:
            return None


class OrderDescriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderDescription
        fields = ('description',)


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
    flight_code = serializers.CharField(source='box.flight.code', default=None, read_only=True)
    cost_kgs = serializers.IntegerField(required=False)

    class Meta:
        model = BaseParcel
        fields = (
            'created_at', 'arrived_at', 'track_code', 'barcode', 'client_code', 'phone', 'price', 'weight', 'cost_usd',
            'cost_kgs', 'status', 'status_label', 'flight_code',
        )
