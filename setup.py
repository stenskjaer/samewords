# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='samewords',
      version='0.0.1',
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
