# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("timescaledbapp", "0001_initial"),
    ]

    operations = [

        migrations.RunSQL(
            sql=[(
                "CREATE TABLE public.timescaledbapp_timeserie ( \
                    timestamp timestamp NOT NULL, \
                    value float NOT NULL, \
                    channel_id int4 NOT NULL, \
                    chunk_id int4 NOT NULL, \
                    CONSTRAINT timescaledbapp_timeserie_pkey PRIMARY KEY (timestamp, channel_id, chunk_id), \
                    CONSTRAINT timescaledbapp_timeserie_timestamp_channel_chunk_unique UNIQUE (timestamp, channel_id, chunk_id) \
                );\
                SELECT create_hypertable('timescaledbapp_timeserie', 'timestamp', chunk_time_interval => interval '1 hours');"
            )],

            reverse_sql=[(
                "DROP TABLE public.timescaledbapp_timeserie;"
            )]
        ),


    ]
