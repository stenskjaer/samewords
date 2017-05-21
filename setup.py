# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from reledmac_samewords import __version__

setup(name='reledmac_samewords',
      version=__version__,
      packages=find_packages(),
      install_requires=[
          'pytest==3.0.7',
      ],
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ],

      description='Package for disambiguation of terms in LaTeX reledmac encoded editions.',
      url='https://github.com/stenskjaer/reledmac_samewords',
      author='Michael Stenskjær Christensen',
      author_email='michael.stenskjaer@gmail.com',
      license='MIT',
)
