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


try:
    from xoeuf.addons.xopgi_mail_threads.utils import (
        is_automatic_response,
        get_automatic_response_type,
        NOT_AUTOMATIC_RESPONSE,
        AUTO_REPLIED,
        AUTO_GENERATED,
        DELIVERY_STATUS_NOTIFICATION,
        DISPOSITION_NOTIFICATION,
    )
except ImportError:
    def is_automatic_response(message):
        '''Check if the message seems to be auto-responded.

        Review RFC 3834, for better understanding this method.

        In the sense of this method "automatic response" include:

        - Any sort of message that is sent automatically in reply to a
          message. RFC 3834.

        - Any sort of message indicating the disposition of another message.
          Example is a notification of a message being read by any of its
          recipients.  RFC 3798.

        - Any sort of message indicating the status of a message delivery by
          the message transport system. Example is a bounce for no valid
          address given.  RFC 3464

        '''
        return bool(get_automatic_response_type(message))

    def get_automatic_response_type(message):
        '''Get automatic response type.

        Types of "automatic responses" match descriptions in RFC 3834, 3798
        and 3464 which are included in `is_auto_submitted`:func:.

        Return any of the constants:

        NOT_AUTOMATIC_RESPONSE

            The message is not an automatic response.  It's a logically false
            value.

        AUTO_REPLIED

            The message was auto-replied.

        AUTO_GENERATED

            The message was auto-generated.


        DELIVERY_STATUS_NOTIFICATION

            The message is an delivery status notification.

        DISPOSITION_NOTIFICATION

            The message is a disposition notification.

        '''
        how = message.get('Auto-Submitted', '').lower()
        content_type = message.get('Content-Type', '')
        if how.startswith('auto-replied'):
            return AUTO_REPLIED
        elif how.startswith('auto-generated'):
            return AUTO_GENERATED
        elif message['X-Autoreply'] == 'yes' and 'In-Reply-To' in message:
            # Some MTAs also include this, but I will refuse them unless an
            # In-Reply-To is provided.
            return AUTO_REPLIED
        elif content_type.startswith('message/report'):
            if 'report-type=delivery-status' in content_type:
                return DELIVERY_STATUS_NOTIFICATION
            elif 'report-type=disposition-notification' in content_type:
                return DISPOSITION_NOTIFICATION
        return NOT_AUTOMATIC_RESPONSE

    NOT_AUTOMATIC_RESPONSE = 0  # Keep this False-like.
    AUTO_REPLIED = 1
    AUTO_GENERATED = 2
    DELIVERY_STATUS_NOTIFICATION = 3
    DISPOSITION_NOTIFICATION = 4
