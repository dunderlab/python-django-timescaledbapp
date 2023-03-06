from django.views.generic.base import TemplateView


from .models import Measure, Channel, TimeSerie
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import MeasureSerializer, ChannelSerializer, TimeSerieSerializer


########################################################################
class MeasureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Measure.objects.all()
    serializer_class = MeasureSerializer


########################################################################
class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


########################################################################
class TimeSerieViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TimeSerie.objects.all()
    serializer_class = TimeSerieSerializer
