#!/usr/bin/env python

from setuptools import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    # #  don't do this unless you want a globally visible script
    # scripts=['bin/myscript'], 
    packages=['nl_robot_console'],
    package_dir={'': 'src'}
)

setup(**d)
