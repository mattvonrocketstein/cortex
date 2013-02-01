"""
"""
from goulash.net import is_port_open
from cortex.core.util import report
from cortex.core.data import CORTEX_PORT_RANGE,LOOPBACK_HOST
class PortChooser(object):
    @property
    def port(self):
        if hasattr(self, '_port'):
            return self._port ##= 1338
        report("Choosing port")
        for x in range(*CORTEX_PORT_RANGE):
            report("Trying: ",x)
            if not is_port_open(x, LOOPBACK_HOST):
                self._port = x
                return x
