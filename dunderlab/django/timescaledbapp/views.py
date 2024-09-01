import json
from typing import Any, Optional

import numpy as np
from django.views import View
from django.db import connection, connections
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework import viewsets, status
from rest_framework.response import Response

from .paginators import Paginationx64, TimeseriePagination
from .filters import ChannelFilter, MeasureFilter, SourceFilter
from .permissions import (
    AdminPermission,
    ConsumerPermission,
    ProduserPermission,
)
from .models import (
    TimeSerie,
    Channel,
    Measure,
    Chunk,
    Source,
    Measure,
    Channel,
)
from .serializers import (
    SourceSerializer,
    MeasureSerializer,
    ChannelSerializer,
    ChunkSerializer,
    TimeserieSerializer,
    TimeserieBrowsableSerializer,
)


# ----------------------------------------------------------------------
@csrf_exempt
def ping_view(request):
    if request.method == 'GET':
        data = request.GET.get('data', '')
        client_timestamp = float(request.GET.get('timestamp', 0))
        server_timestamp = float(timezone.now().timestamp())

    elif request.method == 'POST':
        params = json.loads(request.body.decode('utf8'))
        data = str(params.get('data', ''))
        client_timestamp = float(params.get('timestamp', 0))
        server_timestamp = float(timezone.now().timestamp())

    return JsonResponse(
        {
            'client_timestamp': str(client_timestamp),
            'server_timestamp': str(server_timestamp),
            'bytes': len(data),
        }
    )


@method_decorator(csrf_exempt, name='dispatch')
class TimescaleConfigView(View):

    def get(self, request, *args, **kwargs):
        try:
            with connections['timescaledb'].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT range_start, range_end
                    FROM timescaledb_information.chunks
                    WHERE hypertable_name = 'timescaledbapp_timeserie'
                    ORDER BY range_start DESC
                    LIMIT 1;
                    """
                )
                result = cursor.fetchone()
                if result:
                    range_start, range_end = result
                    # Calcular el chunk_interval como la diferencia entre range_end y range_start
                    chunk_interval = range_end - range_start
                    if chunk_interval.seconds == 0:
                        chunk_interval = (
                            'Not enought data to calculate chunk interval'
                        )
                    else:
                        chunk_interval = self.convert_seconds(
                            chunk_interval.seconds
                        )
                else:
                    chunk_interval = "No chunks found"

            with connections['timescaledb'].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT config->>'drop_after' as retention_interval
                    FROM timescaledb_information.jobs
                    WHERE hypertable_name = 'timescaledbapp_timeserie'
                    AND proc_name = 'policy_retention';
                    """
                )
                retention_result = cursor.fetchone()
                if retention_result:
                    retention_interval = retention_result[0]
                    # retention_interval = self.time_to_seconds(
                    #     retention_interval
                    # )
                    # retention_interval = self.convert_seconds(
                    #     retention_interval
                    # )

            return JsonResponse(
                {
                    'status': 'success',
                    'chunk_interval': chunk_interval,
                    'retention_interval': retention_interval,
                }
            )
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, status=500
            )

    def post(self, request, *args, **kwargs):

        chunk_interval = request.POST.get(
            'chunk_interval',
            json.loads(request.body.decode('utf8')).get(
                'chunk_interval', settings.TIMESCALEDB_CHUNK_INTERVAL
            ),
        )
        retention_interval = request.POST.get(
            'retention_interval',
            json.loads(request.body.decode('utf8')).get(
                'retention_interval', settings.TIMESCALEDB_RETENTION_INTERVAL
            ),
        )

        try:
            # Usa la conexión a la base de datos 'timescaledb'
            with connections['timescaledb'].cursor() as cursor:
                # Actualizar el intervalo de chunks
                cursor.execute(
                    f"SELECT set_chunk_time_interval('timescaledbapp_timeserie', INTERVAL '{chunk_interval}');"
                )

                # Verificar si existe una política de retención antes de intentar eliminarla
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM timescaledb_information.jobs
                    WHERE hypertable_name = 'timescaledbapp_timeserie'
                    AND proc_name = 'policy_retention';
                    """
                )
                retention_policy_exists = cursor.fetchone()[0] > 0

                if retention_policy_exists:
                    # Eliminar la política de retención existente
                    cursor.execute(
                        f"SELECT remove_retention_policy('timescaledbapp_timeserie');"
                    )

                # Añadir la nueva política de retención
                cursor.execute(
                    f"SELECT add_retention_policy('timescaledbapp_timeserie', INTERVAL '{retention_interval}');"
                )

            return JsonResponse(
                {
                    'status': 'success',
                    'chunk_interval': chunk_interval,
                    'retention_interval': retention_interval,
                }
            )
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, status=500
            )

    def convert_seconds(self, seconds):
        hours = round(seconds / 3600)
        days = round(seconds / 86400)

        if days >= 1:
            return f"{days} days"
        elif hours >= 1:
            return f"{hours} hours"
        else:
            return f"{seconds} seconds"

    def time_to_seconds(self, time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s


########################################################################
class CustomCreateViewSet:
    """
    Base ViewSet to support custom create actions for models. Inherits from `viewsets.ModelViewSet`.

    Methods
    -------
    create(self, request: Request, *args: Any, **kwargs: dict) -> Response
        Creates model instance(s) using request data.
    """

    # ----------------------------------------------------------------------
    def create(
        self, request: Request, *args: Any, **kwargs: dict
    ) -> Response:
        """
        Create model instance(s) using request data.

        Parameters
        ----------
        request : Request
            The request containing the data.
        *args : Any
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        Response
            The response containing serialized data or errors.
        """
        data = request.data
        serializer = self.get_serializer(
            data=data, many=isinstance(data, list)
        )

        if serializer.is_valid():
            serializer.save()
            if isinstance(serializer, TimeserieSerializer) or isinstance(
                getattr(serializer, 'child', None), TimeserieSerializer
            ):
                return Response({}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


########################################################################
class SourceViewSet(CustomCreateViewSet, viewsets.ModelViewSet):
    """
    ViewSet for the Source model. Inherits from `CustomCreateViewSet` and `viewsets.ModelViewSet`.

    Attributes
    ----------
    queryset : QuerySet
        The QuerySet containing all Source instances.
    serializer_class : Type[SourceSerializer]
        The serializer class used to serialize and deserialize Source instances.
    pagination_class : Type[Paginationx64]
        The pagination class used to paginate the QuerySet.
    """

    lookup_value_regex = "[^/]+"
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    pagination_class = Paginationx64
    filter_backends = [DjangoFilterBackend]
    permission_classes = [
        AdminPermission | ConsumerPermission | ProduserPermission
    ]
    filterset_class = SourceFilter

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "Source"

    # ----------------------------------------------------------------------
    def get_view_description(self, html: Optional[bool] = False) -> str:
        text = "The SourceViewSet API endpoint. Allows CRUD operations for sources."
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


########################################################################
class MeasureViewSet(CustomCreateViewSet, viewsets.ModelViewSet):
    """
    ViewSet for the Measure model. Inherits from `CustomCreateViewSet` and `viewsets.ModelViewSet`.

    Attributes
    ----------
    queryset : QuerySet
        The QuerySet containing all Measure instances.
    serializer_class : Type[MeasureSerializer]
        The serializer class used to serialize and deserialize Measure instances.
    pagination_class : Type[Paginationx64]
        The pagination class used to paginate the QuerySet.
    """

    lookup_value_regex = "[^/]+"
    queryset = Measure.objects.all()
    serializer_class = MeasureSerializer
    pagination_class = Paginationx64
    filter_backends = [DjangoFilterBackend]
    permission_classes = [
        AdminPermission | ConsumerPermission | ProduserPermission
    ]
    filterset_class = MeasureFilter

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "Measure"

    # ----------------------------------------------------------------------
    def get_view_description(self, html: Optional[bool] = False) -> str:
        text = "The MeasureViewSet API endpoint. Allows CRUD operations for measures."
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


########################################################################
class ChannelViewSet(CustomCreateViewSet, viewsets.ModelViewSet):
    """
    ViewSet for the Channel model. Inherits from `CustomCreateViewSet` and `viewsets.ModelViewSet`.

    Attributes
    ----------
    queryset : QuerySet
        The QuerySet containing all Channel instances.
    serializer_class : Type[ChannelSerializer]
        The serializer class used to serialize and deserialize Channel instances.
    pagination_class : Type[Paginationx64]
        The pagination class used to paginate the QuerySet.
    """

    lookup_value_regex = "[^/]+"
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = Paginationx64
    filter_backends = [DjangoFilterBackend]
    permission_classes = [
        AdminPermission | ConsumerPermission | ProduserPermission
    ]
    filterset_class = ChannelFilter

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "Channel"

    # ----------------------------------------------------------------------
    def get_view_description(self, html: Optional[bool] = False) -> str:
        text = "The ChannelViewSet API endpoint. Allows CRUD operations for channels."
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text

    # ----------------------------------------------------------------------
    def delete(self, request, *args, **kwargs):
        filter_kwargs = request.data.copy()

        if not filter_kwargs:
            return Response(
                {'status': 'Bad Request: No filters provided'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filtered_queryset = self.filterset_class(
            data=filter_kwargs, queryset=self.queryset
        )

        if not filtered_queryset.is_valid():
            return Response(
                {'status': 'Bad Request: Invalid filters'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset_to_delete = filtered_queryset.qs

        if queryset_to_delete.exists():
            queryset_to_delete.delete()
            return Response(
                {'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'status': 'Not Found'}, status=status.HTTP_404_NOT_FOUND
            )


########################################################################
class ChunkViewSet(CustomCreateViewSet, viewsets.ModelViewSet):
    """
    ViewSet for the Chunk model. Inherits from `CustomCreateViewSet` and `viewsets.ModelViewSet`.

    Attributes
    ----------
    queryset : QuerySet
        The QuerySet containing all Chunk instances.
    serializer_class : Type[ChunkSerializer]
        The serializer class used to serialize and deserialize Chunk instances.
    pagination_class : Type[Paginationx64]
        The pagination class used to paginate the QuerySet.
    """

    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer
    pagination_class = Paginationx64
    permission_classes = [
        AdminPermission | ConsumerPermission | ProduserPermission
    ]

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "Chunk"

    # ----------------------------------------------------------------------
    def get_view_description(self, html: Optional[bool] = False) -> str:
        text = "The ChunkViewSet API endpoint. Allows CRUD operations for chunks."
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


########################################################################
class TimeserieViewSet(CustomCreateViewSet, viewsets.ModelViewSet):
    """
    ViewSet for the Timeserie model. Inherits from `CustomCreateViewSet` and `viewsets.ModelViewSet`.

    Attributes
    ----------
    queryset : QuerySet
        The QuerySet containing all Timeserie instances.
    serializer_class : Type[TimeserieSerializer]
        The serializer class used to serialize and deserialize Timeserie instances.
    pagination_class : Type[TimeseriePagination]
        The pagination class used to paginate the QuerySet.

    Methods
    -------
    list(self, request: Request, *args: Any, **kwargs: dict) -> Response
        Lists all instances of the Timeserie model or filters them according to the request.
    """

    serializer_class = TimeserieSerializer
    queryset = TimeSerie.objects.all()
    permission_classes = [
        AdminPermission | ConsumerPermission | ProduserPermission
    ]
    pagination_class = TimeseriePagination

    # ----------------------------------------------------------------------
    def get_view_name(self) -> str:
        return "Chunk"

    # ----------------------------------------------------------------------
    def get_view_description(self, html=False) -> str:
        text = "The TimeserieViewSet API endpoint. Allows CRUD operations for timeseries."
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text

    # ----------------------------------------------------------------------
    def list(self, request: Request, *args: Any, **kwargs: dict) -> Response:
        """
        List all instances of the Timeserie model or filter them according to the request.

        Parameters
        ----------
        request : Request
            The request containing any potential filters.
        *args : Any
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        Response
            The paginated response containing serialized data.
        """

        # Default response for browsable API
        if not request.accepted_renderer.format == 'json':
            self.paginator.page_size = 128
            return Response(
                TimeserieBrowsableSerializer(
                    self.paginator.paginate_queryset(self.queryset, request),
                    many=True,
                ).data
            )

        stats = request.query_params.get('stats', False)
        stats = stats in ['True', 'true', True, '1']
        times = request.query_params.get('timestamps', 'single absolute')
        times_relative = 'relative' in times
        times_absolute = 'absolute' in times
        if not times_absolute and not times_relative:
            times_absolute = True

        # Measure
        source_label = request.query_params.get('source')
        measure_label = request.query_params.get('measure')
        measure = Measure.objects.select_related('source').get(
            source_id=source_label, label=measure_label
        )

        # Channel
        channels = Channel.objects.filter(measure=measure)
        # channels = Channel.objects.select_related('measure').filter(measure=measure)
        channel_dict = {channel.label: channel for channel in channels}
        channel_labels = request.query_params.getlist(
            'channels', channel_dict.keys()
        )

        # Chunks
        chunks_labels = request.query_params.getlist('chunks', None)
        chunks = Chunk.objects.filter(
            measure=measure, label__in=chunks_labels
        )
        # chunks = Chunk.objects.select_related('measure').filter(measure=measure, label__in=chunks_labels)

        # Timeseries for chunks
        timeseries_by_channel_list = []
        if chunks_labels:
            timeseries_by_chunk = [
                (chunk.label, chunk.timeseries.all()) for chunk in chunks
            ]
            timeseries_by_chunk = self.paginate_queryset(timeseries_by_chunk)
            for chunk, timeserie in timeseries_by_chunk:
                timeseries_by_channel = {}
                for channel_label in channel_labels:
                    channel = channel_dict[channel_label]
                    times_values = [
                        (ts.timestamp, ts.value)
                        for ts in timeserie.filter(channel=channel)
                    ]
                    timestamps, values = zip(*times_values)
                    timeseries_by_channel[channel_label] = {
                        'timestamps': np.array(timestamps),
                        'values': np.array(values),
                    }
                timeseries_by_channel_list.append(
                    (chunk, timeseries_by_channel)
                )

        # Timeseries
        else:
            timeseries_by_channel = {}
            for channel_label in channel_labels:
                channel = channel_dict[channel_label]

                timeserie = self.paginate_queryset(channel.timeseries.all())

                if timeserie:
                    times_values = [
                        (ts.timestamp, ts.value) for ts in timeserie
                    ]
                    timestamps, values = zip(*times_values)
                    timeseries_by_channel[channel_label] = {
                        'timestamps': np.array(timestamps),
                        'values': np.array(values),
                    }
            timeseries_by_channel_list.append((None, timeseries_by_channel))

        results_list = []
        for chunk, timeseries_by_channel in timeseries_by_channel_list:
            times_single = 'single' in times
            times_ = not times in ['False', 'false', False, '0']

            results = {
                'source': source_label,
                'measure': measure_label,
                'chunk': chunk,
                'timestamps': (
                    {} if (stats or not times_single and times_) else []
                ),
                'values': {},
            }

            if not chunk:
                results.pop('chunk')

            for i, channel_label in enumerate(timeseries_by_channel):

                timeseries = timeseries_by_channel[channel_label]

                if stats:  # Stats for values
                    results['values'][channel_label] = {
                        "avg_value": timeseries['values'].mean(),
                        "std_value": timeseries['values'].std(),
                        "max_value": timeseries['values'].max(),
                        "min_value": timeseries['values'].min(),
                        "sum_value": timeseries['values'].sum(),
                    }

                    # timeseries_stats = TimeSerie.objects.filter(channel=channel).aggregate(
                    # avg_value=Avg('value'),
                    # std_value=StdDev('value'),
                    # max_value=Max('value'),
                    # min_value=Min('value'),
                    # sum_value=Sum('value'),
                    # )

                else:  # Values
                    results['values'][channel_label] = timeseries['values']

                if times_ or times_single:

                    if stats:
                        times_r = [
                            t.timestamp() for t in timeseries['timestamps']
                        ]
                        timestamp_stats = {
                            "tmin": times_r[0],
                            "tmax": times_r[-1],
                            "duration": times_r[-1] - times_r[0],
                            "avg_diff_timestamp": np.diff(times_r).mean()
                            * 1000,
                            "std_diff_timestamp": np.diff(times_r).std()
                            * 1000,
                            "max_diff_timestamp": np.diff(times_r).max()
                            * 1000,
                            "min_diff_timestamp": np.diff(times_r).min()
                            * 1000,
                        }
                        if times_single:
                            results['timestamps'] = timestamp_stats
                        else:
                            results['timestamps'][
                                channel_label
                            ] = timestamp_stats

                    else:
                        if times_absolute:
                            timestamps = timeseries['timestamps']
                        elif times_relative:
                            timestamps = [
                                t.timestamp() * 1000
                                for t in timeseries['timestamps']
                            ]

                        if times_single:
                            results['timestamps'] = timestamps
                        else:
                            results['timestamps'][channel_label] = timestamps

                    if (
                        times_single
                    ):  # to prvent multiple iterations for `single` timestamps
                        times_single = False
                        times_ = False

            results_list.append(results)

        if len(results_list) > 1:
            serializer = self.get_serializer(results_list, many=True)
        else:
            serializer = self.get_serializer(results_list[0])

        return self.get_paginated_response(serializer.data)

    # ----------------------------------------------------------------------
    def create(self, request, format=None):
        """"""
        serializer = TimeserieSerializer(
            data=request.data, many=isinstance(request.data, list)
        )
        if serializer.is_valid():
            response = serializer.save()
            if isinstance(response, list):
                return Response(
                    [r.data for r in response], status=status.HTTP_200_OK
                )
            return response
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
