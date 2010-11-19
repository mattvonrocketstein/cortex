""" cortex.services.beacon
"""

from cortex.services import Service
from cortex.core.util import report, console

GROUP = '227.3.3.7'
PORT = 31337

class MudPee(Service):
    """
    MUlticastDnsPeerdiscovery service
      Will broadcast JSON dicts in the form of
      {
          "name": "universe_name",

          services: {
              "name": True || {"option1": "value1" ...}
              .
              .
          }
      }

    Operations:
      <start>: initiates service advertisements and listens for them
      <stop>:  Stops the service
    """

    def stop(self):
        """ """
        Service.stop(self)
        report('Stopping MudPee', self)

    def start(self):
        """
        """
        report('Starting MudPee', self)
