from .models import Measure, Channel, TimeSerie
from rest_framework import serializers


########################################################################
class MeasureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measure
        fields = ['device_id', 'device_name', 'location', 'sample_rate']


########################################################################
class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Channel
        fields = ['measure', 'name']


########################################################################
class TimeSerieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TimeSerie
        fields = ['channel', 'time', 'value']


