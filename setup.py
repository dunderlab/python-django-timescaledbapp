import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='dunderlab-timescaledbapp',
    version='0.1.17',
    packages=['dunderlab.django.timescaledbapp', 'dunderlab.api'],
    author='Yeison Cardona',
    author_email='yencardonaal@unal.edu.co',
    maintainer='Yeison Cardona',
    maintainer_email='yencardonaal@unal.edu.co',
    download_url='https://github.com/dunderlab/python-django.timescaledbapp',
    install_requires=[
        'psycopg2-binary',
        'aiohttp',
        'numpy',
    ],
    scripts=[
        "cmd/timescaledbapp_create",
    ],
    include_package_data=True,
    license='BSD-2-Clause',
    description="Django TimeScale DB App",
    long_description=README,
    long_description_content_type='text/markdown',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.10',
    ],
)
