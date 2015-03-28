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

ESCAPED = {'@': '=.', '=': '=='}
UNESCAPED = {val: key for key, val in ESCAPED.items()}


def encode(email):
    '''Encodes an email so that is could be embedded in another address.

    Examples::

       >>> encode('some@address.com')
       'some=.address.com'

       >>> encode('some=.thing@=else.com=')
       'some==.thing=.==else.com=='

    Decoding this should be done with `decode`:func:.

    '''
    # Escaping: "@" becomes "=."; "=" becomes "=="; a single "." does not
    # needs to be escaped.  If the email contains "=." it will turn into "==."
    # the second "=" won't be regarded as an escape char.
    from six import integer_types as position
    res = ''
    while email:
        pos = min(find(email, ch) for ch in ESCAPED.keys())
        if isinstance(pos, position):
            res += email[:pos] + ESCAPED[email[pos]]
            email = email[pos+1:]
        else:
            res += email
            email = ''
    return res


def decode(vmail):
    '''Decodes an embedded email.

    Examples::

       >>> decode(encode('some@address.com'))
       'some@address.com'

       >>> decode(encode('some==thing=@else.com='))
       'some==thing=@else.com='

       >>> decode(encode('some=.@=else.com'))
       'some=.@=else.com'

    '''
    from six import integer_types as position
    res = ''
    while vmail:
        pos = min(find(vmail, ch) for ch in UNESCAPED.keys())
        if isinstance(pos, position):
            res += vmail[:pos] + UNESCAPED[vmail[pos:pos+2]]
            vmail = vmail[pos+2:]
        else:
            res += vmail
            vmail = ''
    return res


# Helper to allow min(find()...) in our main algorithm to work.  This is
# basically a position which is always bigger than any other position, but
# that is not an integer.
class NotFoundType(object):
    def __lt__(self, x):
        return False
    def __gt__(self, x):
        return True
    def __bool__(self, x):
        return False
    __nonzero__ = __bool__

NotFound = NotFoundType()


def find(s, what):
    res = s.find(what)
    return res if res >= 0 else NotFound
