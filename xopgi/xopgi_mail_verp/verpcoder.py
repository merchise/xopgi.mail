#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# verpcoder
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-26

'''Encodes/Decodes an email for inclusion in the Return-Path.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


def encode(email):
    '''Encodes an email so that is could be embedded in another address.

    Examples::

       >>> encode('some@address.com')
       'some=address.com'

       >>> encode('some=thing@else.com=')
       'some==thing=else.com=='

    Decoding this should be done with `decode`:func:.

    '''
    pass


def decode(verpmail):
    '''Decodes an embedded email.

    Examples::

       >>> decode(encode('some@address.com'))
       'some@address.com'

       >>> decode(encode('some=thing@else.com='))
       'some=thing@else.com='

    Decoding this should be done with `decode`:func:.

    '''
    pass
