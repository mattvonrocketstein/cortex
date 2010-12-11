""" cortex.contrib.promela.net

      Network/Communication functionality defined by Promela

"""

from cortex.contrib.promela import channels

def exclusive_channel(name):
    """ Exclusive receive (xr) and send (xs) on channels

               xr Transfer;
               xs Channel;

            in some process, declares that this process is the only one
            to receive messages on Transfer and the only one to send on
            Channel.

            It is a run-time error if during analysis it turns out that
            some other process receives from Transfer or sends to Channel.

            See Reductions for more detail.
    """
    instructions = InstructionSet()
    return channels.Exclusive(name)
