# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from samewords import __version__

setup(name='samewords',
      version=__version__,
      packages=find_packages(),
      install_requires=[
          'pytest==3.0.7',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing :: Markup :: LaTeX',
      ],
      description='Package for disambiguation of terms in LaTeX reledmac encoded editions.',
      url='https://github.com/stenskjaer/reledmac_samewords',
      author='Michael Stenskjær Christensen',
      author_email='michael.stenskjaer@gmail.com',
      license='MIT',
)
