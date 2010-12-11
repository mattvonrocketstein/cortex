class Channel:
    """ Channel operations

           q!var1,const,var2,...  or, equivalently  q!var1(const,var2,...)
           q?var1,const,var2,...  or, equivalently  q?var1(const,var2,...)

         Are the standard channel operations; the first is a send statement,
         the second a receive. Here, q denotes a channel and the list
         var1,const,var2,... should be compatible with the channel's message
         type. For a send or receive to be enabled, q has to be initialized.
         Furthermore, if the channel is buffered, a send is enabled if the
         buffer is not full; a receive is enabled if the buffer is non-empty.
         On an unbuffered channel, a send (receive) is enabled only if there
         is a corresponding receive (send) that can be executed simultaneously.
         A receive statement executes by reading the oldest message on the
         channel; if the channel is unbuffered, it reads the message of the
         simultaneously executing send statement. A send statement executes by
         putting its message in the buffer (if there is one). Note that a channel
         operation on an unbuffered channel can only execute if a matching
         operation executes simultaneously.

         Constants in the list of a receive, constrain its enabledness by
         forcing the corresponding values in the oldest message (or matching
         send) to be the same; if not, the receive is blocked.

         It is possible to use a local or global variable to likewise
         constrain a channel operation's enabledness:

             q?var1,eval(var2),var3

         blocks in case a matching send's 2nd value does not equal the value
         of var2. Note that the value of var2 is not changed.
    """
    def __init__(self, name):
        self.name = name

class Exclusive(Channel):
    def xr(self, data):
        pass

    def xs(self, data):
        pass

class BufferChannel(Channel):
    """ For buffered channels, there are additional operations:

           * q?[var1,const,var2] returns true (i.e. a non-zero value)
             precisely if the corresponding receive operation would
             be enabled.

           * q?<var1,const,var2> like a standard receive operation
              except that the message is not removed from the buffer.

           * q!!var1,const,var sorted send; it inserts its message
             into the buffer immediately ahead of (so that it will
             be younger than) the oldest message that succeeds it
             in numerical, lexicographic order.


           * q??var1,const,var random receive; it executes if there
             is some message in the buffer for which it is enabled
             and then retrieves the oldest such message.

           * q??[var1,const,var2] returns true (i.e. a non-zero value)
             precisely if the corresponding receive operation would be
             enabled.

           * q??<var1,const,var2> like a standard random receive
             operation except that the message is not removed from
             the buffer.

         The behavior of buffered channels can be influenced by the Spin
         command line switch -m: in that case, send actions on a channel
         do not block if the channnel's buffer is full; instead, messages
         send when the buffer is full are lost.
    """
