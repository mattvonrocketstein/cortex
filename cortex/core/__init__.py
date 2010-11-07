""" cortex.core.__init__
"""

def handle_command(options):
    """ """
    exec(options.command)

def handle_file(fname):
    """ """
    print "cortex: assuming this is a file.."
    execfile(fname)
