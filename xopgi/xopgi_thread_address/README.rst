Unique Thread Address(xopgi_thread_address)
===========================================
Ensure each mail thread has a unique address to respond to. You must ensure
your MTA accepts dynamic addresses.
The default prefix for a Reply-To address. We suggest to use the same as the
mail.catchall.alias. The Reply-To address is constructed as
``<replyto alias>+<thread index>@<domain>``. Notice we use the "+" to separate
the alias from the thread index, this allows some MTAs to fallback to the
alias should the entire address fail.
