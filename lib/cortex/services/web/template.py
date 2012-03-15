"""
"""
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('cortex.services.web', 'templates'))
def template(name):
    return env.get_template(name + '.html')
