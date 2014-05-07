#!/usr/bin/env python
from setuptools import setup
setup(
    name='oparlvalidator',
    version='0.0.1',
    author='OParl Consortium',
    include_package_data=True,
    extras_require=dict(
        test=[],
    ),
    install_requires=[
        'setuptools',
        'requests==2.2.1',
        'schematics==0.9-4',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': []
    }
)
