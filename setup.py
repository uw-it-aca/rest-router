#!/usr/bin/env python

import os

from distutils.core import setup
import setuptools

setup(name='Rest-Router',
      version='1.0.0',
      license = "Apache 2.0",
      author = "UW-IT ACA",
      author_email = "pmichaud@uw.edu",
      packages=setuptools.find_packages(exclude=["project"]),
      include_package_data=True,  # use MANIFEST.in during install
      url='https://github.com/uw-it-aca/rest-router',
      description='',
      install_requires=['Django==1.9', 'urllib3'],
     )
