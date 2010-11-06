# /home/matt/code/cortex/cortex/core/services/magic.py
import dbus, gobject, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

from cortex.core.util import report
from cortex.core.services import Service
import IPython.Shell

TYPE = "_http._tcp"
def service_resolved(*args):
        print 'service resolved'
        print 'name:', args[2]
        print 'address:', args[7]
        print 'port:', args[8]

def print_error(*args):
        print 'error_handler'
        print args[0]

def myhandler(interface, protocol, name, stype, domain, flags):
        print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)

        if flags & avahi.LOOKUP_RESULT_LOCAL:
                # local service, skip
                pass

class Client(Service):
    """ Beacon Service:
          start:
          stop:
    """

    def _post_init(self):
        self.is_stopped=False

    def stop(self):
        """ """
        self.is_stoppped = True
        self.gloop.quit()

    def iterate(self):
        #print 'client iterating'
        while not self.is_stopped:
            self.loop_context.iteration(True)
        #self.universe.reactor.callLater(1, self.iterate)

    def play(self):
        setup_client()
        #self.universe.reactor.callLater(1, gobject.MainLoop().run)
        loop = gobject.MainLoop()
        gobject.threads_init()
        self.gloop = loop
        self.loop_context = self.gloop.get_context()
        #self.universe.reactor.callInThread(self.gloop.run)
        self.universe.reactor.callInThread(self.iterate)
        #
        #import threading
        #threading.Thread(target=gobject.MainLoop().run).start()
        #self.iterate()
        # Handle commands here
        #self.loop_context.iteration(True)

        #
        return self

def setup_client():
    """ """
    loop = DBusGMainLoop()
    bus = dbus.SystemBus(mainloop=loop)
    server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
                             'org.freedesktop.Avahi.Server')
    sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
            server.ServiceBrowserNew(avahi.IF_UNSPEC,
                avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))),
            avahi.DBUS_INTERFACE_SERVICE_BROWSER)
    sbrowser.connect_to_signal("ItemNew", myhandler)

def main():
    """ """
    def callback():
        print 'callback'
    setup_client()
    gobject.threads_init()
    loop = gobject.MainLoop()
    gobject.timeout_add(1,callback)
    loop.run()

    #context = loop.get_context()
    #while 1:
    #    print '3'
    #    # Handle commands here
    #    context.iteration(True)

if __name__=='__main__':
    main()
