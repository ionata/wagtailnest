#!/usr/bin/env python
import io

from setuptools import setup, find_packages

from src.wagtailnest import __version__


with open('README.rst', 'r') as f:
    readme = f.read()

requirements = []

with io.open('requirements.txt', encoding='utf-8') as fyle:
    for line in fyle.readlines():
        parsed = line.strip('\n').strip()
        if line != '' and line[0] != '#':
            requirements.append(line)


setup(
    name='wagtailnest',
    version=__version__,
    description='A RESTful Wagtail enclosure',
    long_description=readme,
    author='Ionata Digital',
    author_email='webmaster@ionata.com.au',
    url='https://github.com/ionata/wagtailnest',
    packages=find_packages('src'),
    install_requires=requirements,
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
