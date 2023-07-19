from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from dunderlab.django.timescaledbapp.models import Source, Measure, Channel, Chunk, TimeSerie


# ----------------------------------------------------------------------
def permissions(codenames):
    """"""
    return [Permission.objects.get(codename=codename) for codename in codenames]


# ----------------------------------------------------------------------
def permissions_all(codename):
    """"""
    return list(Permission.objects.filter(codename__contains=codename))


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):

        api_groups = {
         'api_admin': (
             permissions_all('source'),
             permissions_all('measure'),
             permissions_all('channel'),
             permissions_all('chunk'),
             permissions_all('timeserie'),
         ),

         'api_consumer': (
             permissions(['view_source']),
             permissions(['view_measure']),
             permissions(['view_channel']),
             permissions(['view_chunk']),
             permissions(['view_timeserie']),
         ),

         'api_produser': (
             permissions(['view_source']),
             permissions(['view_measure']),
             permissions(['view_channel']),
             permissions(['view_chunk', 'add_chunk']),
             permissions(['view_timeserie', 'add_timeserie']),

         ),
         'api_transformer': (
             # create_permission(Source, 'source', 'all'),
             # create_permission(Measure, 'measure', 'all'),
             # create_permission(Channel, 'channel', 'all'),
             # create_permission(Chunk, 'chunk', 'all'),
             # create_permission(TimeSerie, 'timeserie', 'all'),
         ),
            }

        for group_name in api_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            for permission in api_groups[group_name]:
                if isinstance(permission, list):
                    [group.permissions.add(p) for p in permission]
                else:
                    group.permissions.add(permission)
