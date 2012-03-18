""" cortex.services.web.template
"""
from jinja2.ext import with_, autoescape
from jinja2 import Environment, PackageLoader
from cortex.contrib.pygments_extension import PygmentsExtension
env = Environment(loader=PackageLoader('cortex.services.web', 'templates'),
                  extensions=[with_,autoescape,
                              PygmentsExtension, ])

def template(name):
    return env.get_template(name + '.html')
