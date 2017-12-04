#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


class IRogueBounceProber:
    def __call__(self, msg):
        '''Probe if the message is a rogue bounce.

        This method should return None if the message is not a rogue bounce.
        If the message is a rogue bounce it must return a dictionary with the
        following keys:

        :thread_index: The index of the thread.
        :failures:  A list of the addresses that failed.

        :param msg:  The message.
        :type msg: email.message.Message

        '''
