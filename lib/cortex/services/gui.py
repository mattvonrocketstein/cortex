""" cortex.services.gui
      http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
"""
from twisted.internet import gtk2reactor # for gtk-2.0
gtk2reactor.install()


import gtk
from cortex.services import Service
from cortex.core.data import EVENT_T
from cortex.core.util import report, console
from cortex.services.terminal.terminal import IPShellTwisted, IPY_ARGS
from cortex.mixins import LocalQueue
from cortex.util.decorators import constraint

import gtk
from ipython_view import *
import pango

import platform
if platform.system()=="Windows":
    FONT = "Lucida Console 9"
else:
    FONT = "Luxi Mono 10"

class GUI(Service):
    """ """

    def start(self):
        W = gtk.Window()
        W.set_size_request(750,550)
        W.set_resizable(True)
        S = gtk.ScrolledWindow()
        S.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        V = IPythonView()
        V.modify_font(pango.FontDescription(FONT))
        V.set_wrap_mode(gtk.WRAP_CHAR)
        V.show()
        S.add(V)
        S.show()
        W.add(S)
        color = gtk.gdk.color_parse('#234fdb')
        W.modify_bg(gtk.STATE_NORMAL, color)

        W.show()
        W.connect('delete_event',lambda x,y:False)
        W.connect('destroy',lambda x:gtk.main_quit())
        #gtk.main()

if __name__=='__main__':
    from twisted.internet import reactor
    GUI().start()
    reactor.run( )
