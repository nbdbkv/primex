from rest_framework import serializers

from flight.models import Media, BaseParcel


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Media
        fields = ('title', 'media',)


class StatisticsSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BaseParcel
        fields = ('code', 'status', 'status_label',)


class BaseParcelSearchSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BaseParcel
        fields = ('code', 'track_code', 'weight', 'consumption', 'status', 'status_label',)
