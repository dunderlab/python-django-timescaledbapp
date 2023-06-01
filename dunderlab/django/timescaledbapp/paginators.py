"""
=====================================
Timescaledbapp Pagination Components
=====================================

This module provides pagination classes for the timescaledbapp's API views. These classes
are used to control how API results are split into individual pages of data.

Classes
-------

.. rubric:: TrialPagination

This class is a custom pagination class that inherits from Django Rest Framework's PageNumberPagination.
It sets the page size to 16 and allows the client to override this with the `page_size` query parameter.
The maximum allowed page size is 10000.

.. rubric:: TimeseriePaginator

A custom Paginator class specifically for time series data. It overrides the `count` property to return
the count of the first channel in the object list.

.. rubric:: TimeseriePagination

This class is a custom pagination class specifically for time series data. It sets the page size to 1024
and allows the client to override this with the `page_size` query parameter.
It uses the TimeseriePaginator class for Django's paginator.

.. rubric:: Paginationx64

This class is a custom pagination class that sets the page size to 64.
This can be used for any view where a page size of 64 is desired.

Each of these classes is used by the API views to control how many objects are returned in each API response.

"""

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from django.utils.functional import cached_property


########################################################################
class TrialPagination(PageNumberPagination):
    """A custom pagination class that allows page sizes up to 10000."""
    page_size = 16
    page_size_query_param = 'page_size'
    max_page_size = 10000


########################################################################
class TimeseriePaginator(Paginator):
    """A custom paginator class for time series data."""

    @cached_property
    # ----------------------------------------------------------------------
    def count(self):
        """Returns the count of the first channel in the object list."""

        if self.object_list:

            if isinstance(self.object_list[0], tuple):
                return len(self.object_list)
            else:
                return self.object_list[0].channel.count

        else:
            return 0


########################################################################
class TimeseriePagination(PageNumberPagination):
    """A custom pagination class specifically for time series data."""
    page_size = 1024
    page_size_query_param = 'page_size'
    django_paginator_class = TimeseriePaginator


########################################################################
class Paginationx64(PageNumberPagination):
    """A custom pagination class that sets the page size to 64."""
    page_size = 64

