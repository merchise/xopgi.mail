============================================
 Breaking Cycles of auto-submitted messages
============================================

We try to avoid the scenario where two subscribes a single object engage in a
never-ending cycle of auto-submitted messages:

#. Some user sends a message to A and B

#. Party A sends an auto-submitted reply.  It does so by complying with
   up-to-date RFCs (e.g uses Auto-Submitted and replies to Return-Path).

#. Odoo resends the message to B

#. B's auto-responders send the automatic message to Odoo (again with good
   headers)

#. Odoo resends to A

#. A's auto-responders send the automatic message to Odoo

\.\.\. and so on.


Both bounces and auto-replies SHOULD be sent to the Return-Path.  The VERP
addon (xopgi_mail_verp) disregards auto-responded replies (otherwise they
would appear as Undelivered messages).

This addon catches auto-responses and avoid to relay them willy nilly.
