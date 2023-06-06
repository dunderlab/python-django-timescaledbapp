"""
================================
Timescaledbapp Serializer Module
================================

This module provides serializers for the timescaledbapp's API views.
These classes are used to control how API request and response data is converted
from complex types (like model instances) to Python native datatypes that can
then be easily rendered into JSON.

Functions
---------

.. rubric:: insert_batch

This function is a helper that allows to perform bulk create operation for
given model with specified batch size. The default batch size is 1000.

Classes
-------

.. rubric:: SourceSerializer

This class provides a serializer for the Source model. It includes all fields
in the source model in the serialized representation.

.. rubric:: MeasureSerializer

This class provides a serializer for the Measure model. It also includes a 'source'
field which is serialized from the 'source_id' field of the model.

.. rubric:: ChannelSerializer

This class provides a serializer for the Channel model. It also includes 'measure'
and 'source' fields. It overrides the 'create' method to pop 'measure' and 'source'
from validated data and get the measure instance before creating the channel.

.. rubric:: ChunkSerializer

This class provides a serializer for the Chunk model. It also includes a 'measure'
field. It overrides the 'create' method to pop 'measure' from validated data and
get the measure instance before creating the chunk.

.. rubric:: DictOrListField

This is a custom serializer field that can serialize both lists and dictionaries.
It delegates to a child field to serialize the individual items in the list or
dictionary.

.. rubric:: TimestampField

This is a custom serializer field for timestamps. If the input is a float, it
converts it to a datetime iso format string.

.. rubric:: TimeserieSerializer

This class provides a serializer for creating TimeSerie instances. It includes 'source',
'measure', 'timestamps', 'values' and 'chunk' fields. It overrides the 'create' method
to pop 'measure', 'source' and 'chunk' from validated data, get the related measure
and chunk instances, create TimeSerie instances and perform a bulk insert.

Each of these classes and function plays a critical role in handling API request
and response data in the Timescaledbapp.

"""

from concurrent.futures import ThreadPoolExecutor
import numpy as np
from datetime import datetime
from django.utils.timezone import make_aware
from .models import Measure, TimeSerie, Channel, Chunk
from typing import Type, Any, Union
from rest_framework import serializers, status
from .models import Source, Measure, Channel
from django.db.models import Model
from rest_framework.response import Response
from django.db.utils import IntegrityError


# ----------------------------------------------------------------------
def insert_batch(model: Type[Model], objects: list[Model], batch_size: int = 1000) -> None:
    """
    Inserts a batch of objects into the database.

    Parameters
    ----------
    model : Type[Model]
        The model class of the objects.
    objects : list[Model]
        The objects to be inserted.
    batch_size : int, optional
        The size of the batch to be inserted, by default 1000
    """
    return model.objects.bulk_create(objects, batch_size=batch_size)


########################################################################
class SourceSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Source model.

    The class converts complex data types into Python datatypes,
    so they can then be easily rendered into JSON, XML, or other content types.
    """
    class Meta:
        model = Source
        fields = ['label', 'name', 'location', 'device', 'protocol', 'version', 'description', 'created']


########################################################################
class MeasureSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Measure model.

    The class converts complex data types into Python datatypes,
    so they can then be easily rendered into JSON, XML, or other content types.
    """
    source = serializers.CharField(source='source_id')

    class Meta:
        model = Measure
        fields = ['label', 'name', 'description', 'source']


########################################################################
class ChannelSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Channel model.

    The class converts complex data types into Python datatypes,
    so they can then be easily rendered into JSON, XML, or other content types.
    Also, it provides a method to create new Channel instances.
    """
    measure = serializers.CharField()
    source = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Channel
        fields = ['label', 'name', 'unit', 'sampling_rate', 'description', 'source', 'measure']

    # ----------------------------------------------------------------------
    def create(self, validated_data: dict[str, Any]) -> Channel:
        """
        Creates a Channel instance using the provided validated data.

        Parameters
        ----------
        validated_data : dict[str, Any]
            The validated data to use for creating the Channel.

        Returns
        -------
        Channel
            The created Channel instance.
        """
        measure_params = {
            'label': validated_data.pop('measure'),
            'source__label': validated_data.pop('source'),
        }
        measure = Measure.objects.get(**measure_params)
        channel = Channel.objects.create(measure=measure, **validated_data)
        return channel

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['measure'] = instance.measure.label
        ret['source'] = instance.measure.source.label
        return ret


########################################################################
class ChunkSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Chunk model.

    The class converts complex data types into Python datatypes,
    so they can then be easily rendered into JSON, XML, or other content types.
    Also, it provides a method to create new Chunk instances.
    """
    measure = serializers.CharField(source='measure.label')

    class Meta:
        model = Chunk
        fields = ['label', 'measure']

    # ----------------------------------------------------------------------
    def create(self, validated_data: dict[str, Any]) -> Chunk:
        """
        Creates a Chunk instance using the provided validated data.

        Parameters
        ----------
        validated_data : dict[str, Any]
            The validated data to use for creating the Chunk.

        Returns
        -------
        Chunk
            The created Chunk instance.
        """
        measure_params = {
            'label': validated_data.pop('measure'),
        }
        measure = Measure.objects.get(**measure_params)
        chunk = Chunk.objects.create(measure=measure, **validated_data)
        return chunk


########################################################################
class DictOrListField(serializers.Field):
    """
    A custom field serializer that supports both dictionary and list data types.

    It validates and transforms incoming data into an internal value for use in serializer methods.
    """

    # ----------------------------------------------------------------------
    def __init__(self, child: Any, *args: Any, **kwargs: Any) -> None:
        """
        Initializes a new instance of the DictOrListField class.

        Parameters
        ----------
        child : Any
            The type of the child elements.
        *args : Any
            Variable length argument list.
        **kwargs : Any
            Arbitrary keyword arguments.
        """
        self.child = child
        super().__init__(*args, **kwargs)

    # ----------------------------------------------------------------------
    def to_representation(self, value: Any) -> Any:
        """
        Converts a Python object into a data type that can then be rendered into JSON.

        Parameters
        ----------
        value : Any
            The Python object to be converted.

        Returns
        -------
        Any
            The data type that can be rendered into JSON.
        """
        return value

    # ----------------------------------------------------------------------
    def to_internal_value(self, data: Union[list[Any], dict[Any, Any]]) -> Union[list[Any], dict[Any, Any]]:
        """
        Validates the incoming data and returns the converted form.

        Parameters
        ----------
        data : Union[list[Any], dict[Any, Any]]
            The data to be validated and converted.

        Returns
        -------
        Union[list[Any], dict[Any, Any]]
            The validated and converted form of the data.
        """
        if isinstance(data, list):
            return [self.child.to_internal_value(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.child.to_internal_value(value) for key, value in data.items()}
        else:
            raise serializers.ValidationError("Invalid data type. Expected a dictionary or a list.")


########################################################################
class TimestampField(serializers.Field):
    """
    A custom field serializer for timestamp data.

    It validates and transforms incoming data into an internal value for use in serializer methods.
    """

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the TimestampField class.

        Parameters
        ----------
        *args : Any
            Variable length argument list.
        **kwargs : Any
            Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    # ----------------------------------------------------------------------
    def to_representation(self, value: Any) -> Any:
        """
        Converts a Python object into a data type that can then be rendered into JSON.

        Parameters
        ----------
        value : Any
            The Python object to be converted.

        Returns
        -------
        Any
            The data type that can be rendered into JSON.
        """
        return value

    # ----------------------------------------------------------------------
    def to_internal_value(self, data: float) -> str:
        """
        Validates and converts the incoming timestamp data to an ISO-formatted string.

        Parameters
        ----------
        data : Union[float, str]
            The timestamp data to be validated and converted.

        Returns
        -------
        str
            The validated and converted timestamp.
        """
        if isinstance(data, float):
            data = datetime.fromtimestamp(data).isoformat()
        return data


########################################################################
class TimeserieSerializer(serializers.Serializer):
    """
    Serializer for the TimeSerie model.

    The serializer defines the fields that get deserialized or converted to JSON output.
    It also provides a method for creating new TimeSerie instances.
    """

    source = serializers.CharField(required=False, allow_blank=True)
    measure = serializers.CharField()
    timestamps = DictOrListField(child=TimestampField())
    values = serializers.DictField(child=DictOrListField(child=serializers.FloatField()))
    chunk = serializers.CharField(required=False, allow_blank=True)

    # ----------------------------------------------------------------------
    def create(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """
        Creates TimeSerie instances using the provided validated data.

        Parameters
        ----------
        validated_data : dict[str, Any]
            The validated data to use for creating the TimeSerie instances.

        Returns
        -------
        dict[str, Any]
            A status message indicating the success of the operation and the number of objects created.
        """
        measure = Measure.objects.select_related('source').get(source_id=validated_data.pop('source'), label=validated_data.pop('measure'))
        timestamps = np.array(validated_data.pop('timestamps'))
        values = validated_data.pop('values')

        # chunk, _ = Chunk.objects.get_or_create(measure=measure, label=validated_data.pop('chunk', 'default'))

        if chunk_label := validated_data.pop('chunk', False):
            chunk = Chunk.objects.create(measure=measure, label=validated_data.pop('chunk', chunk_label))
        else:
            chunk, _ = Chunk.objects.get_or_create(measure=measure, label=validated_data.pop('chunk', 'default'))

        if isinstance(timestamps[0], float):
            timestamps = np.array(list(map(lambda t:
                                           make_aware(datetime.fromtimestamp(t)), timestamps)))

        channels = Channel.objects.filter(measure=measure)
        channel_dict = {channel.label: channel for channel in channels if channel.label in values.keys()}

        # for channel_label in channel_dict:
            # channel = channel_dict[channel_label]
            # channel.count = channel.count + len(timestamps)
            # channel.save()

        timeseries = []
        for channel_label in values:
            channel = channel_dict[channel_label]
            for i, value in enumerate(values[channel_label]):
                timeserie_params = {
                    'timestamp': timestamps[i],
                    'value': value,
                    'channel': channel,
                    'chunk': chunk,
                }
                timeseries.append(TimeSerie(**timeserie_params))

        try:

            insert_batch(TimeSerie, timeseries, batch_size=1000)
        except IntegrityError:
            return Response({
                "status": "fail",
                "message": "Objects can not be created.",
            },
                status=status.HTTP_403_FORBIDDEN, content_type='application/json')

        for channel_label in channel_dict:
            channel = channel_dict[channel_label]
            channel.count = channel.count + len(timestamps)
            channel.save()

        return Response({
            "status": "success",
            "message": "Your data has been successfully saved.",
            "objects_created": len(timeseries),
        },
            status=status.HTTP_201_CREATED, content_type='application/json')
