""" cortex.core.services.magic
"""
import time
import IPython.Shell
import multiprocessing
import dbus, gobject, avahi

from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
from multiprocessing import Process, Value, Array
from cortex.core.services.zeroconf import ZeroconfService

from cortex.core.util import report
from cortex.core.services import Service
from cortex.core.data import AVAHI_TYPE as TYPE

def service_resolved(*args):
    """ """
    print 'service resolved'
    print 'name:', args[2]
    print 'address:', args[7]
    print 'port:', args[8]

def print_error(*args):
    """ """
    print 'error_handler'
    print args[0]


class Client(Service):
    """ Zeroconf Client Service:
          start: begin looking for peers
          stop:  stop looking for peers
    """
    def _post_init(self):
        """ """
        self.is_stopped=False

    def stop(self):
        """ """
        self.is_stoppped = True
        self.gloop.quit()

    def iterate(self):
        """
            self.universe.reactor.callLater(1, self.iterate)
        """
        while not self.is_stopped:
            self.loop_context.iteration(True)

    def play(self):
        """
            #import threading
            #threading.Thread(target=gobject.MainLoop().run).start()
            #self.iterate()
            # Handle commands here
            #self.loop_context.iteration(True)
            #self.universe.reactor.callLater(1, gobject.MainLoop().run)
            #self.universe.reactor.callInThread(self.gloop.run)
        """
        self.setup_client()
        loop = gobject.MainLoop()
        gobject.threads_init()
        self.gloop = loop
        self.loop_context = self.gloop.get_context()
        self.universe.reactor.callInThread(self.iterate)
        return self

    def setup_client(self):
         """ """
         loop = DBusGMainLoop()
         bus = dbus.SystemBus(mainloop=loop)
         server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
                                  'org.freedesktop.Avahi.Server')
         sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                 server.ServiceBrowserNew(avahi.IF_UNSPEC,
                     avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))),
                 avahi.DBUS_INTERFACE_SERVICE_BROWSER)
         sbrowser.connect_to_signal("ItemNew", self.peer_found)

    def peer_found(self, interface, protocol, name, stype, domain, flags):
         """ """
         if name!=self.universe.name:
             # TODO: push this onto system events list
             notice="Found peer '%s' type '%s' domain '%s' " % (name, stype, domain)
             self.universe.push_event(notice)
             if flags & avahi.LOOKUP_RESULT_LOCAL:
                 # local service, skip
                 pass

class AutodiscoveryServer(Service):
    """ Zeroconf-Server Service:
          start: ..
          stop:  ..
    """
    def _post_init(self):
        """ """
        self.zeroconf = ZeroconfService(name=self.universe.name, port=3000)

    def stop(self):
        """
        super(Service,self).stop()
        """
        self.v.value = 0
        report('Server is dying')
        self.started = False
        self.is_stopped = True
        try:
            self.zeroconf.unpublish()
        except AttributeError:
            pass

    def iterate(self, v):
        """ """
        self.started = True,
        self.zeroconf.publish()
        while v.value == 1:
            time.sleep(1)

    def play(self):
        """
        """
        self.v = Value('d',1) # Shared memory for the exit-ttest
        self.p = Process(target=self.iterate, args=[self.v])
        self.p.start()
        return self

