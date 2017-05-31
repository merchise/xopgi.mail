Same server policy(xopgi_mailservers)
=====================================
A transport that tries to send a message using an SMTP server that "matches"
the original receiver of the first message in the thread.

This works like this:

- You may have several registered SMTP servers and also several matching
  incoming servers (though optional).

- Suppose you have an SMTP server that connects identifies itself (SMTP
  authentication) with "john.doe@gamil.com".

- You receive a message To: john.doe@gamil.com.  That creates a new thread
  (say a CRM lead).

- Then when responding to that thread, we'll choose the SMTP server that
  matches (one of) the recipients of the original message that created the
  thread.

  Also the From address of the message will be set to that of the outgoing
  SMTP server.
