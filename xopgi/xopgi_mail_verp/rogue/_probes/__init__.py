#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Probes.

Probes must have a single ``__call__(self, message)``.  See the
'interfaces.py' file for document.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


# The router use the probes in the order given by __all__, so you may prefer a
# probe other another.
__all__ = [
    'NautaProbe',
    'AHabanaProbe',
    # Keep this at the bottom
    # 'FLUFLProbe',
]

from .nauta import NautaProbe
from .ahabana import AHabanaProbe
# from .heuristics import FLUFLProbe
