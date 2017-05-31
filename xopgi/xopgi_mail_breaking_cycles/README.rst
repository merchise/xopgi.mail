Breaking Cycles sending messages(xopgi_mail_breaking)
=====================================================
This pair of Router & Transport avoid the mail-sending cycles when two
or more parties in a single thread have auto-responders:

1- Party A sends a message
2- Odoo resends to Party B
3- The party B's auto-responders send the automatic message to Odoo
4- Odoo resends to Party A
5- The Party A's auto-responders send the automatic message to Odoo.

This, of course, assumes that both Party A and B have buggy auto-responders
that auto-respond to messages which are themselves auto-submitted.

The VERP Transport already bails out when the message being sent is an
auto-submitted one.  So this addon plays well with VERP.

What we do is that when sending auto-submitted messages we replace the
Return-Path, Reply-To, Sender and From with a 'breaking-cycle' address, if a
auto-submitted message is received for any 'breaking-cycle' address is
simply ignored.
