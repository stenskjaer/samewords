# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='lbp_print',
      version=__version__,
      packages=find_packages(),
      install_requires=[
          'docopt==0.6.2',
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
