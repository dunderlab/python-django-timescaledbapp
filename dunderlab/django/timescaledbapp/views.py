from django.views.generic.base import TemplateView
from .models import Metric, AnotherMetricFromTimeScaleModel, TemperatureReading
from datetime import datetime


########################################################################
class HomeView(TemplateView):
    template_name = "dunderlab_timescaledb/home.html"

    # ----------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        """"""
        context = super().get_context_data(**kwargs)
        TemperatureReading.objects.create(temperature=72.5, location='San Francisco', time=datetime.now())

        return context
