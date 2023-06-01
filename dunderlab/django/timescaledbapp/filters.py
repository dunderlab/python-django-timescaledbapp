import django_filters
from .models import Channel, Measure, Source
# from django.db.models import Q


class SourceFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(field_name='label')
    name = django_filters.CharFilter(field_name='name')
    location = django_filters.CharFilter(field_name='location')
    device = django_filters.CharFilter(field_name='device')
    protocol = django_filters.CharFilter(field_name='protocol')
    version = django_filters.CharFilter(field_name='version')
    description = django_filters.CharFilter(field_name='description')
    created = django_filters.DateTimeFilter(field_name='created')

    class Meta:
        model = Source
        fields = ['label', 'name', 'location', 'device', 'protocol', 'version', 'description', 'created']


class MeasureFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(field_name='label')
    name = django_filters.CharFilter(field_name='name')
    description = django_filters.CharFilter(field_name='description')
    source = django_filters.CharFilter(field_name='source__label')

    class Meta:
        model = Measure
        fields = ['label', 'name', 'description', 'source']


class ChannelFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(field_name='label')
    name = django_filters.CharFilter(field_name='name')
    measure = django_filters.CharFilter(field_name='measure__label')
    source = django_filters.CharFilter(field_name='measure__source__label')

    class Meta:
        model = Channel
        fields = ['label', 'name', 'measure', 'source']


# class TrialFilter(django_filters.FilterSet):
    # trial_class = django_filters.CharFilter(field_name='trial_class__label')
    # channel = django_filters.CharFilter(field_name='channel__label')
    # source = django_filters.CharFilter(field_name='source__source')

    # class Meta:
        # model = Trial
        # fields = ['trial_class', 'source', 'channel']


# class TimeSerieFilter(django_filters.FilterSet):
    # # trial_class = django_filters.CharFilter(field_name='trial_class__label')
    # channel = django_filters.CharFilter(field_name='channel__label')
    # source = django_filters.CharFilter(field_name='channel__measure__source__name')
    # time_gte = django_filters.DateFilter(field_name='time', lookup_expr='gte')
    # time_lte = django_filters.DateFilter(field_name='time', lookup_expr='lte')

    # class Meta:
        # model = TimeSerie
        # fields = ['channel', 'source', 'time_gte', 'time_lte']

    # @classmethod
    # def filter_by_dates(cls, queryset, start_date, end_date):
        # # Use Q objects to combine multiple conditions with OR
        # q1 = Q(time__gte=start_date)
        # q2 = Q(time__lte=end_date)
        # return queryset.filter(q1 & q2)
