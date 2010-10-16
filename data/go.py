""" go.py: second phase init
"""
from twisted.internet import stdio
from twisted.protocols import basic

from cortex import core

class Terminal(basic.LineReceiver):
    from os import linesep as delimiter

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

def main():
    stdio.StandardIO(Echo())
    from twisted.internet import reactor
    reactor.run()

if __name__ == '__main__':
    main()
