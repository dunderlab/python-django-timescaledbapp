"""
======================
Timescaledbapp Models
======================

This module provides the Django models for the timescaledbapp.

Models
------

.. rubric:: Source

Represents the source of a measurement. Each source has an ID, a name, a
location, a device, a protocol, a version, a description, and a timestamp
indicating when it was created.

.. rubric:: Measure

Represents a measure taken by a source. Each measure has a label, a name, a
description, and is linked to a specific source.

.. rubric:: Channel

Represents a channel of a measure. Each channel has a label, a name, a unit, a
sampling rate, a description, is linked to a specific measure, and has a count
of the number of times it has been used.

.. rubric:: Chunk

Represents a chunk of a measure. Each chunk has a label and is linked to a
specific measure.

.. rubric:: TimeSerie

Represents a time series data point. Each data point has a timestamp, a value,
is linked to a specific channel and chunk.

Each of these models corresponds to a table in the database, and each attribute
of a model corresponds to a field in the table. The relationships between the
models (such as the ForeignKey fields) represent database relationships (such
as foreign key constraints).

"""

from django.db import models
from django.utils.translation import gettext as _


########################################################################
class Source(models.Model):
    """
    The Source model represents a source of measures. Each source has a unique ID and additional details
    including its name, location, device, protocol, version, and a description.
    """
    label = models.CharField('Source ID', primary_key=True, unique=True, max_length=2**6)
    name = models.CharField('Name', max_length=2**8)
    location = models.CharField('Location', max_length=2**8, null=True, blank=True)
    device = models.CharField('Device', max_length=2**8, null=True, blank=True)
    protocol = models.CharField('Protocol', max_length=2**8, null=True, blank=True)
    version = models.CharField('Version', max_length=2**4, null=True, blank=True)
    description = models.TextField('Description', max_length=2**15, null=True, blank=True)
    created = models.DateTimeField('Created', auto_now_add=True)


########################################################################
class Measure(models.Model):
    """
    The Measure model represents a specific measure made by a source. Each measure has a label, name,
    description, and a reference to its source. A source can have multiple measures.
    """
    label = models.CharField('Label', max_length=2**4)
    name = models.CharField('Name', max_length=2**8)
    description = models.TextField('Description', max_length=2**15, null=True, blank=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='measures')

    class Meta:
        unique_together = ('source', 'label')


########################################################################
class Channel(models.Model):
    """
    The Channel model represents a specific channel of a measure. Each channel has a label, name, unit,
    sampling rate, description, count, and a reference to its measure. A measure can have multiple channels.
    """
    label = models.CharField('Label', max_length=2**4)
    name = models.CharField('Name', max_length=2**8)
    unit = models.CharField('Unit', max_length=2**8)
    sampling_rate = models.FloatField('Sampling rate')
    description = models.TextField('Description', max_length=2**15, null=True, blank=True)
    measure = models.ForeignKey('Measure', on_delete=models.CASCADE, related_name='channels')
    count = models.IntegerField('Count', default=0)

    class Meta:
        unique_together = ('measure', 'label')


########################################################################
class Chunk(models.Model):
    """
    The Chunk model represents a specific chunk of a measure. Each chunk has a label and a reference to its measure.
    A measure can have multiple chunks.
    """
    label = models.CharField(max_length=2**5, null=True, blank=True)
    measure = models.ForeignKey('Measure', on_delete=models.CASCADE, related_name='chunks')

    # class Meta:
        # unique_together = ('label', 'measure')


########################################################################
class TimeSerie(models.Model):
    """
    The TimeSerie model represents a time series of data. Each record in the time series has a timestamp, a value,
    and references to a channel and a chunk.
    """
    timestamp = models.DateTimeField('Timestamp', primary_key=True)
    value = models.FloatField('Value')
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='timeseries', db_column='channel_id', db_index=True)
    chunk = models.ForeignKey('Chunk', on_delete=models.CASCADE, related_name='timeseries', db_column='chunk_id', db_index=True)

    class Meta:
        """
        This Meta class within TimeSerie model sets additional options for this model:
        - managed: If False, no database table creation, modification, or deletion operations will be performed for this model.
        - db_table: Specifies the name of the database table.
        - unique_together: This option is a list of lists, where each sublist is a group of fields that must be unique when considered together.
        """
        managed = False
        db_table = 'timescaledbapp_timeserie'
        unique_together = ('timestamp', 'channel', 'chunk')
