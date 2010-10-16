""" cortex.core.terminal
"""
from os import linesep as delimiter
from twisted.protocols import basic

class Terminal(basic.LineReceiver):
    """ terminal input """
    def say(self,msg, *args, **kargs):
        """ """
        self.transport.write(str(msg)+' '+str(args)+ ' '+str(kargs))

    def connectionMade(self):
        self.transport.write('>>> ')

    def lineReceived(self, line):
        try:
            self.sendLine('Eval: ' + str(eval(line)))

        except Exception,e:
            self.sendLine('Error Evaluating.')

            try:
                exec(line)
                self.sendLine('Executed..')
                self.sendLine(str(locals()))
            except Exception,e:
                [self.sendLine(line) for line in str(e).split('\n')]
        self.transport.write('>>> ')
