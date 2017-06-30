#!/usr/bin/env python
import io

from setuptools import setup, find_packages

from src.wagtailnest import __version__


with open('README.rst', 'r') as f:
    readme = f.read()

requirements = []


setup(
    name='wagtailnest',
    version=__version__,
    description='A RESTful Wagtail enclosure',
    long_description=readme,
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/wagtailnest',
    packages=find_packages('src'),
    install_requires=[
        ## Setup/running requirements
        'django-environ~=0.4.3',

        ## Core requirements
        'django~=1.11.0',
        'djangorestframework~=3.6.2',
        'djangorestframework-filters~=0.10.0',
        'djangorestframework-jwt',
        'django-allauth~=0.27.0',
        'django-cors-headers~=1.2.2',
        'django-csv-utils',
        'django-enumfields',
        'django-filter~=1.0.2',
        'django-minimal-user==0.0.1',
        'django-rest-auth~=0.9.0',
        'django-rest-swagger~=2.0.6',
        'django-revproxy==0.9.13',
        'wagtail~=1.10.0',
        'django-anymail[mailgun]~=0.5.0',
        'django-extensions',

        ## Tasking
        'celery[redis]',

        ## Python extras
        'pytz',
        'python-dateutil',
        'Pillow',
        'requests==2.15.1',
        'geopy',
        'faker',
        'pygments',
        'markdown',
        'beautifulsoup4',
    ],
    package_dir={'': 'src'},
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
