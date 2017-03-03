===================
 One line subjects
===================

Ensure one line subjects on outgoing messages.

For some reasons (I think it's when resending messages), sometimes the Subject
header contains a new-line char and that confuses Python and it refuses to
send the message.  This transport avoids the issue.
