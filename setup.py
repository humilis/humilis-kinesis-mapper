"""Setuptools entrypoint."""
import codecs
import os

from setuptools import setup, find_packages

from humilis_kinesis_mapper import __version__

dirname = os.path.dirname(__file__)

long_description = (
    codecs.open(os.path.join(dirname, "README.rst"), encoding="utf-8").read() + "\n" +
    codecs.open(os.path.join(dirname, "AUTHORS.rst"), encoding="utf-8").read() + "\n" +
    codecs.open(os.path.join(dirname, "CHANGES.rst"), encoding="utf-8").read()
)

setup(
    name="humilis-kinesis-mapper",
    include_package_data=True,
    packages=find_packages(include=['humilis_kinesis_mapper', 'humilis_kinesis_mapper.*']),
    version=__version__,
    author="Anatoly Bubenkov, FindHotel and others",
    author_email="developers@innovativetravel.eu",
    url="http://github.com/humilis/humilis-kinesis-mapper",
    license="MIT",
    description="Humilis kinesis stream mapper plugin",
    long_description=long_description,
    install_requires=[
        "humilis>=0.4.1",
        "lamdautils>=0.2.3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2"
    ],
    zip_safe=False,
    entry_points={
        "humilis.layers": [
            "kinesis-mapper=humilis_kinesis_mapper.plugin:get_layer_path"]}
)
