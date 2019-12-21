# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from samewords import __version__

with open("README.md") as file:
    long_description = str(file.read())

setup(
    name="samewords",
    version=__version__,
    packages=find_packages(),
    install_requires=["regex==2018.8.17"],
    test_requires=["pytest==5.3.2"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    description="Package for disambiguation of identical terms in critical "
    "editions in LaTeX with reledmac.",
    url="https://github.com/stenskjaer/samewords",
    author="Michael Stenskjær Christensen",
    author_email="michael.stenskjaer@gmail.com",
    license="MIT",
    long_description=long_description,
    entry_points={"console_scripts": ["samewords=samewords.cli:main"]},
)
