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

import logging
logger = logging.getLogger(__name__)
del logging


class FLUFLProbe(object):
    def __call__(self, msg):
        from flufl.bounce import scan_message
        failed_addresses = scan_message(msg)
        if failed_addresses:
            message_id = msg['Message-Id']
            logger.warn(
                'Possible bounce: %s',
                message_id,
                extra=dict(
                    message_details=msg.items(),
                    failed_addresses=failed_addresses
                )
            )
