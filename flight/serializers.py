from rest_framework import serializers

from flight.models import Media, BaseParcel, Contact


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Media
        fields = ('title', 'image', 'video',)


class StatisticsSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BaseParcel
        fields = ('code', 'status', 'status_label',)


class BaseParcelSearchSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BaseParcel
        fields = ('created_at', 'arrived_at', 'code', 'track_code', 'weight', 'consumption', 'status', 'status_label',)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ('social', 'icon',)
