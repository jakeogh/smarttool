# -*- coding: utf-8 -*-

import fastentrypoints
from setuptools import find_packages, setup

dependencies = ["click"]

config = {
    "version": "0.1",
    "name": "smarttool",
    "url": "https://github.com/jakeogh/smarttool",
    "license": "ISC",
    "author": "Justin Keogh",
    "author_email": "github.com@v6y.net",
    "description": "Device S.M.A.R.T. functions",
    "long_description": __doc__,
    "packages": find_packages(exclude=['tests']),
    "package_data": {"smarttool": ['py.typed']},
    "include_package_data": True,
    "zip_safe": False,
    "platforms": "any",
    "install_requires": dependencies,
    "entry_points": {
        "console_scripts": [
            "smarttool=smarttool.smarttool:cli",
        ],
    },
}

setup(**config)