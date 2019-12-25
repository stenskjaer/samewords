#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package for annotating references to potentially ambiguous words in critical
editions made with LaTeX and reledmac.
"""
import os

__all__ = ["brackets", "cli", "core", "document", "matcher", "settings", "tokenize"]
__root__ = os.path.dirname(os.path.realpath(__file__))
__version__ = "0.5.6"

import samewords.core
