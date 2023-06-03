# TimeScaleDB App

TimeScaleDB App is a Django-based web application that provides an API for managing and querying time-series data. This application utilizes RealTimeDB, a time-series database built atop PostgreSQL, for efficient storage and analysis of time-series data. With custom pagination classes and viewsets, the TimeScaleDB App delivers a powerful and flexible way to interact with Source, Measure, Channel, and TimeSerie models.

## Features

- API endpoints for managing and querying time-series data
- Custom pagination classes for more efficient data retrieval
- Custom viewset mixin enabling creation of multiple objects
- Grouping and aggregation of TimeSerie objects by channel
- Computation of various statistics for aggregated time-series data

## Getting Started

### Installation

1. Clone the repository:

```bash
git clone https://github.com/dunderlab/python-django-timescaledbapp.git
cd python-django-timescaledbapp
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

3. Configure your database settings in the `settings.py` file:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'your_database_host',
        'PORT': 'your_database_port',
    }
}
```

4. Add the required apps to `INSTALLED_APPS` in the `settings.py` file:

```python
INSTALLED_APPS = [
    'django_extensions',
    'rest_framework',
    'dunderlab.django.timescaledbapp.apps.TimeScaleDBConfig',
]
```

5. Include the TimeScaleDB App URLs in your project's `urls.py` file:

```python
urlpatterns = [
    path("timescaledbapp/", include('dunderlab.django.timescaledbapp.urls')),
]
```

### Execution

6. Apply the migrations:

```bash
python manage.py migrate
```

7. Start the development server:

```bash
python manage.py runserver
```

You can now access the TimeScaleDB App API at `http://localhost:8000/`.

## API Endpoints

- `/sources/`: View or edit sources
- `/measures/`: View or edit measures
- `/channels/`: View or edit channels
- `/timeseries/`: View or edit time series with custom behavior for listing and paginating time series data
- `/chunk/`: Handle chunks

## Contributing

If you'd like to contribute to TimeScaleDB App, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Commit your changes to your branch
4. Push your branch to your fork
5. Submit a pull request with a detailed description of your changes

We appreciate your contributions and will review them as soon as possible.

## License

TimeScaleDB App is released under the [MIT License](https://opensource.org/licenses/MIT).



![Database model](https://github.com/dunderlab/python-django-timescaledbapp/raw/main/docs/source/notebooks/_images/myapp_models.png)
