#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='kkhep',
    version='0.0.1',
    description='Helper scripts for making HEP plots with Python.',
    install_requires=[
        'coffea',
        'pyyaml'
      ],
    packages=['kkhep']
)
