""" cortex.services.contrib.autodiscovery

      Your milage may vary with this approach to peer discovery.
      It works somewhat reliably in linux if you can manage to get
      python dbus installed.  However, unregistering announcements
      is problematic, and stale peers seem to be hard to get rid of.
      DBus pretty much spews errors the whole time but you can safely
      ignore them.

      This file will probably be deprecated one day.
"""

import time
import IPython.Shell
import multiprocessing
import dbus, gobject, avahi

from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
from multiprocessing import Process, Value, Array
from cortex.services.contrib.zeroconf import ZeroconfService

from cortex.core.util import report
from cortex.services import Service
from cortex.core.data import AVAHI_TYPE as TYPE

class AutodiscoveryClient(Service):
    """ Zeroconf Client Service:
          start: begin looking for peers
          stop:  stop looking for peers
    """

    def service_resolved(self, *args):
        """
        """
        address = args[7]
        port    = args[8]
        name    = args[2]
        peerMan = self.universe.peers

        if name not in peerMan.registry:
            # TODO: use contrib.hds
            peerMan.registry[str(name)]={}
            report('added registry entry for name',str(name))

        peerMan.registry[name].address = str(address)
        peerMan.registry[name].port = str(port)
        peerMan.registry[name].port = str(port)
        report ('updated registry for name=' + str(name))

    def print_error(self, *errors):
        """ unused, but apparently part of avahi interface """
        for x in errors:
            if 'Timeout reached' in str(x):
                # report('error_handler: timeout') # Do not remove this line
                return
        report('error_handler for name resolution',str(errors) )

    def _post_init(self):
        """ """
        self.is_stopped = False

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
        self.server = self.setup_client()
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
        return server

    def peer_found(self, interface, protocol, name, stype, domain, flags):
        """ handle peer discovery """
        if name != self.universe.name:
            notice="Found Peer @ " + name
            self.universe.push_notice(notice)
            self.universe.peers.register(**dict(name=name,
                                              stype=stype,
                                              domain=domain))
            self.server.ResolveService(interface, protocol, name, stype,
                                       domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                                       reply_handler=self.service_resolved,
                                       error_handler=self.print_error)

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
        self.zeroconf = ZeroconfService(name=self.universe.name,
                                        port=3001, text="testing")

    def stop(self):
        """
        super(Service,self).stop()
        """
        self.v.value = 0
        report('Server is dying')
        self.started = False
        self.is_stopped = True
        self.zeroconf.unpublish()
        #except AttributeError:
        #    pass

    def iterate(self, v):
        """ """
        self.started = True
        try:
            self.zeroconf.publish()
        except DBusException,e:
            if str(e)=='org.freedesktop.DBus.Error.Disconnected: Connection is closed':
                report("Giving up.")
                try:
                    self.p.terminate()
                except AttributeError:
                    """ Processes have a terminate method, but this
                        part appears to be caused by a strange race condition:
                          File "/usr/lib/python2.6/multiprocessing/process.py", line 111, in terminate
                              self._popen.terminate()
                          AttributeError: 'NoneType' object has no attribute 'terminate'

                    """
                    pass

                self.stop()
            else:
                report("squashed dbus error",str(e))
                self.iterate(v)
        while v.value == 1:
            time.sleep(1.3)

    def start(self):
        """ """
        self.v = Value('d',1) # Shared memory for the exit-ttest
        self.p = Process(target=self.iterate, args=[self.v])
        self.universe._procs.append(self.p)
        self.p.start()
        return self
