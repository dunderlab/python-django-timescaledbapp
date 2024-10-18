# Generated manually

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("timescaledbapp", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;",
            reverse_sql="DROP EXTENSION IF EXISTS timescaledb CASCADE;",
        ),
        migrations.RunSQL(
            sql=[
                (
                    f"CREATE TABLE public.timescaledbapp_timeserie ( \
                    timestamp timestamp NOT NULL, \
                    value float NOT NULL, \
                    channel_id int4 NOT NULL, \
                    chunk_id int4 NOT NULL, \
                    CONSTRAINT timescaledbapp_timeserie_pkey PRIMARY KEY (timestamp, channel_id, chunk_id), \
                    CONSTRAINT timescaledbapp_timeserie_timestamp_channel_chunk_unique UNIQUE (timestamp, channel_id, chunk_id) \
                );\
                SELECT create_hypertable('timescaledbapp_timeserie', 'timestamp', chunk_time_interval => interval '{settings.TIMESCALEDB_CHUNK_INTERVAL}');\
                SELECT add_retention_policy('timescaledbapp_timeserie', INTERVAL '{settings.TIMESCALEDB_RETENTION_INTERVAL}', schedule_interval => INTERVAL '{settings.TIMESCALEDB_SCHEDULE_INTERVAL}');"
                )
            ],
            reverse_sql=[("DROP TABLE public.timescaledbapp_timeserie;")],
        ),
    ]
