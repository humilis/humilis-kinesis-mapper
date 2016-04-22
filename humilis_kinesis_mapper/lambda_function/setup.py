# -*- coding: utf-8 -*-
# preprocessor:jinja2

from setuptools import setup, find_packages

setup(
    name="humilis-kinesis-mapper-lambda",
    version="0.0.2",
    packages=find_packages(),
    include_package_data=True,
    # We often need the latest version of boto3 so we include it as a req
    install_requires=[
        "boto3",
        "raven",
        "lambdautils>=0.2.3",
        "werkzeug",
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7"],
    zip_safe=False
)
