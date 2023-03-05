from django.views.generic.base import TemplateView
# from .models import MultiChannelFloat, MultiChannelJson, SingleChannelFloat, SingleChannelJson
from datetime import datetime
from django.utils import timezone


########################################################################
class HomeView(TemplateView):
    template_name = "dunderlab_timescaledb/home.html"

    # ----------------------------------------------------------------------
    def get_context_data(self, **kwargs):
        """"""
        context = super().get_context_data(**kwargs)

        self

        return context
