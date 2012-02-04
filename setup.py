#!/usr/bin/env python

import sys
import os
from setuptools import setup

_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "meteorpy"))
import meteorpy
del sys.path[0]

setup(name='meteorpy',
    version='0.1',
    description="A set of functions useful for meteor science.",
    author='Geert Barentsen',
    author_email='geert@barentsen.be',
    license='GPL'
)
