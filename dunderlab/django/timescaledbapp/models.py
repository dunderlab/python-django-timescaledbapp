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

- Measure: stores metadata of a measuring device.
- Channel: stores the channels of a measuring device.
- TimeSerie: stores the time series data for a specific channel.

The TimeScaleDB App is compatible with Django 3.x and TimeScaleDB 2.x.

For more information on TimeScaleDB, please refer to the official documentation:
https://docs.timescale.com/latest/main/

"""

from django.db import models
from timescale.db.models.models import TimescaleModel


########################################################################
class Measure(models.Model):
    """Model for a measuring device.

    This model stores the metadata of a measuring device such as its unique identifier,
    name, location, unit of measurement and sampling rate.

    Attributes:
        device_id (str): Unique identifier of the device.
        device_name (str): Name of the device.
        location (str): Location where the device is installed.
        unit (str): Unit of measurement.
        sample_rate (float): Sampling rate of the device.
    """

    device_id = models.CharField('Device ID', primary_key=True, max_length=2**8)
    device_name = models.CharField('Device name', max_length=2**8)
    location = models.CharField('Location', max_length=2**8)
    unit = models.CharField('Unit', max_length=2**8)
    sample_rate = models.FloatField('Sample rate')


########################################################################
class Channel(models.Model):
    """Model for a channel of a measuring device.

    This model stores the channels of a measuring device. A channel is a physical
    or virtual input on the device that measures a quantity. For example, a temperature
    sensor may have a channel for the air temperature and another for the surface temperature.

    Attributes:
        measure (ForeignKey): A foreign key to the Measure model.
        name (str): Name of the channel.
    """

    measure = models.ForeignKey('Measure', on_delete=models.CASCADE, related_name='channels')
    name = models.CharField('Name', max_length=2**8)


########################################################################
class TimeSerie(TimescaleModel):
    """Model for a time series data.

    This model stores the time series data for a specific channel of a measuring device.
    Each record contains the value of the data point in the time series and a timestamp
    indicating when the data point was measured.

    Attributes:
        measure (ForeignKey): A foreign key to the Channel model.
        value (float): The value of the data point in the time series.
    """

    measure = models.ForeignKey('Channel', on_delete=models.CASCADE, related_name='timeseries')
    value = models.FloatField()
