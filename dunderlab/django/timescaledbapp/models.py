"""
======================
TimeScaleDB App Models
======================

This Django app is designed to work with TimeScaleDB, a time-series database
built on top of PostgreSQL. The app provides models for storing time-series data
in the database, including information about the measuring device, its channels,
and the time series data itself.

Models
======

- Source: A data source that provides data to the system.
    This model represents a data source that provides data to the system. It
    contains information about the source's ID, creation date, name, location,
    device, protocol, and version.

- Measure: A device that generates data.
    This model represents a device that generates data. It contains information
    about the device's name, as well as a foreign key reference to the data
    source that it belongs to.

- Channel: A specific measurement from a device.
    This model represents a specific measurement from a device. It contains
    information about the measurement's name, unit of measurement, and sample
    rate, as well as a foreign key reference to the device that the measurement
    comes from.

- TimeSerie: A single data point from a specific measurement.
    This model represents a single data point from a specific measurement. It
    contains information about the channel that the data point comes from, as
    well as the value of the data point.

The TimeScaleDB App is compatible with Django 3.x and TimeScaleDB 2.x.

For more information on TimeScaleDB, please refer to the official documentation:
https://docs.timescale.com/latest/main/
"""


from django.db import models
from timescale.db.models.models import TimescaleModel


########################################################################
class Source(models.Model):
    """A data source that provides data to the system.

    This model represents a data source that provides data to the system. It
    contains information about the source's ID,
    creation date, name, location, device, protocol, and version.

    Fields:
        source_id: The unique identifier for the data source.
        created: The date and time when the data source was created.
        name: The name of the data source.
        location: The location of the data source.
        device: The device associated with the data source.
        protocol: The protocol used by the data source.
        version: The version of the data source.
    """

    source_id = models.CharField('Source ID', primary_key=True, max_length=2**8)
    created = models.DateTimeField('Created', auto_now_add=False)
    name = models.CharField('Name', max_length=2**8)
    location = models.CharField('Location', max_length=2**8, null=True, blank=True)
    device = models.CharField('Device', max_length=2**8, null=True, blank=True)
    protocol = models.CharField('Protocol', max_length=2**8, null=True, blank=True)
    version = models.CharField('Version', max_length=2**4, null=True, blank=True)

    # ----------------------------------------------------------------------
    def __str__(self):
        return f'Source({source_id}): {self.source_name} {self.device} {self.version}'


########################################################################
class Measure(models.Model):
    """A measure associated with a data source.

    This model represents a measure associated with a data source. It contains
    information about the measure's name and the source it is associated with.

    Fields:
        source: The data source associated with the measure.
        name: The name of the measure.
    """
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='measures')
    name = models.CharField('Device name', max_length=2**8)

    # ----------------------------------------------------------------------
    def __str__(self):
        """"""
        return f'Measure: {self.name}'


########################################################################
class Channel(models.Model):
    """A channel that belongs to a measure and provides a unit and sample rate.

    This model represents a channel that belongs to a measure and provides information
    about the unit of measurement and sample rate. It is associated with a single measure
    and can be accessed through the `channels` attribute of a measure.

    Fields:
        measure: The measure associated with the channel.
        unit: The unit of measurement for the channel.
        name: The name of the channel.
        sample_rate: The sample rate for the channel in samples per second.
    """

    measure = models.ForeignKey('Measure', on_delete=models.CASCADE, related_name='channels')
    unit = models.CharField('Unit', max_length=2**8)
    name = models.CharField('Name', max_length=2**8)
    sample_rate = models.FloatField('Sample rate')

    # ----------------------------------------------------------------------
    def __str__(self):
        """"""
        return f'Channel: {self.name}'


########################################################################
class TimeSerie(TimescaleModel):
    """A timeseries data point for a channel.

    This model represents a single data point in a timeseries for a channel. It contains
    a reference to the channel it belongs to and the numerical value of the data point.

    Attributes:
        channel: A foreign key reference to the channel the timeseries belongs to.
        value: The numerical value of the data point.
    """

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='timeseries')
    value = models.FloatField()

    # ----------------------------------------------------------------------
    def __str__(self):
        """"""
        return f'Time serie: {self.time}:{self.value}'
