# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from samewords import __version__

setup(name='samewords',
      version=__version__,
      packages=find_packages(),
      install_requires=[
          'pytest==3.0.7',
          'docopt==0.6.2',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Text Processing :: Markup :: LaTeX',
      ],
      description='Package for disambiguation of identical terms in critical editions in LaTeX with reledmac.',
      url='https://github.com/stenskjaer/reledmac_samewords',
      author='Michael Stenskjær Christensen',
      author_email='michael.stenskjaer@gmail.com',
      license='MIT',
      entry_points = {
          'console_scripts' : ['samewords=samewords.cli:main']
      },
)
