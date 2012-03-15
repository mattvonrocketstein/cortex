"""
"""
from jinja2.ext import with_
from jinja2 import Environment, PackageLoader
from cortex.contrib.pygments_extension import PygmentsExtension
env = Environment(loader=PackageLoader('cortex.services.web', 'templates'),
                  extensions=[with_,
                              PygmentsExtension, ])

def template(name):
    return env.get_template(name + '.html')
