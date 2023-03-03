# TimeScaleDB

## Run TimeScaleDB on Docker

### Get Docker TimeScaleDB image


```python
docker pull timescale/timescaledb:latest-pg15
```

### Run container


```python
docker run -d --name timescaledb -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=dunderlab -e POSTGRES_DB=dunderlab_timescale_v3 timescale/timescaledb:latest-pg15
```
