""" cortex.core.rcvr
"""

import os
from binascii import crc32

from twisted.internet.protocol import ServerFactory
from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet

from cortex.core import universe

COMMAND_CODE = '---- >>'

def iscommand(line):
    return line.startswith(COMMAND_CODE)

class FileIOProtocol(basic.LineReceiver):
    """ file receiver """
    def __init__(self):
        self.info = None
        self.outfile = None
        self.remain = 0
        self.crc = 0

    def lineReceived(self, line):
        print ('FileIOProtocol:lineReceived:%s', line)
        self.size = line.strip()
        """

        file_key = uuid.UUID(file_key)
        try:
            session_uuid = uuid.UUID(sess_key)
        except:
            print ('FileIOProtocol:lineReceived Invalid session')
            self.transport.loseConnection()
            return
        """
        #self.job_session = self.factory.sessions.get(session_uuid)
        if False: #        if not self.job_session:
            print ('FileIOProtocol:lineReceived Invalid session')
            self.transport.loseConnection()
            return

        if False: #not self.job_session.active:
            print ('FileIOProtocol:lineReceived Stale session')
            self.transport.loseConnection()
            return

        # [db3l] The original code validates the individual file uuid here
        # resulting in self.job_file as job file object from the session
        #if not self.job_file:
        #    print ('FileIOProtocol:lineReceived Invalid file key')
        #    self.transport.loseConnection()
        #    return

        # Create the upload directory if not already present
        uploaddir = '/tmp/testing_twisted'
        universe['terminal'].say("Using upload dir:",uploaddir)

        if not os.path.isdir(uploaddir):
            os.makedirs(uploaddir)

        self.outfilename = os.path.join(uploaddir, 'data.out')

        print ('FileIOProtocol:lineReceived Receiving into %s',self.outfilename)
        try:
            self.outfile = open(self.outfilename,'wb')
        except Exception, value:
            print ('FileIOProtocol:lineReceived Unable to open file %s '
                         '(%s)', self.outfilename, value)
            self.transport.loseConnection()
            return

        self.remain = int(self.size)
        print ('FileIOProtocol:lineReceived Entering raw mode: %s %s',self.outfile, self.remain)
        self.setRawMode()

    def rawDataReceived(self, data):
        self.remain -= len(data)
        print self.remain,'/',self.size
        self.crc = crc32(data, self.crc)
        self.outfile.write(data)

    def connectionMade(self):
        basic.LineReceiver.connectionMade(self)
        print ('FileIOProtocol:connectionMade')

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        print ('FileIOProtocol:connectionLost')
        if self.outfile:
            self.outfile.close()

        print "remaining:", self.remain
        if self.remain != 0:
            # Problem uploading - discard
            print ('FileIOProtocol:connectionLost remain('+str(self.remain)+')!=0')
            os.remove(self.outfilename)
        """

            else:
                # Update job object with upload status
                self.job_file['uploaded'] = datetime.utcnow()
                self.job_file['size'] = self.size
                self.job_file['crc'] = self.crc
        """

class FileIOFactory(ServerFactory):
    """ file receiver factory """
    protocol = FileIOProtocol

    def __init__(self, db, options={}):
        self.db = db
        self.options = options

class RCVR(basic.LineReceiver):
    """ chat client """
    def connectionMade(self):
        print "Got new client!"
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        print "Lost a client!"
        self.factory.clients.remove(self)

    def parseCommand(self, line):
        print "received command:: ",line

    def commandReceived(self, line):
        return self.parseCommand(line[len(COMMAND_CODE):])

    def lineReceived(self, line):
        if not iscommand(line):
            print "received", repr(line)
            for c in self.factory.clients:
                c.message(line)
        else:
            self.commandReceived(line)

    def message(self, message):
        self.transport.write(message + '\n')
