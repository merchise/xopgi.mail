#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# heuristics
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-03-01

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
logger = logging.getLogger(__name__)
del logging


class FLUFLProbe(object):
    def __call__(self, msg):
        # This probe only
        from flufl.bounce import scan_message
        failed_addresses = scan_message(msg)
        if failed_addresses:
            message_id = msg['Message-Id']
            _logger.warn(
                'Possible bounce: %s',
                message_id,
                extra=dict(
                    message_details=msg.items(),
                    failed_addresses=failed_addresses
                )
            )
