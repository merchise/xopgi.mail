xopgi_evaneos_mailrouter (Integration with emails coming via a Evaneos).
=========================================================================

Improves OpenERP's integration with emails coming via a Evaneos:

 -Evaneos removes the 'References' and 'In-Reply-To' headers.  This makes it
  impossible to OpenERP to "follow the conversation. However, since a single
  "address is used for the same thread, it is possible to assign a thread id
  based of that field.

 -This module assign the thread id of the first message to incoming messages
  when they share the same Evaneos 'From' or 'Sender'.
