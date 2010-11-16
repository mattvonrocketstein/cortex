#!/usr/bin/env python
import os, sys
import subprocess
from setuptools import setup, find_packages
from optparse import OptionParser

BASEDIR = os.path.dirname(os.path.realpath(__file__))

def boot(opts, *args, **options):
    def do(things):
        shell = subprocess.Popen(
                                   'bash',
                                   cwd=BASEDIR, shell=True, universal_newlines=True,
                                   env=os.environ,
                                   stdout=sys.stderr, stderr=sys.stderr, stdin=subprocess.PIPE
                                 )
        shell.communicate(things)
        return shell.poll() == 0

    def die(message):
        sys.stderr.write("=> ERROR: %s\n" % message)
        sys.exit(9000)

    def do_or_die(thing, message):
        sys.stderr.write("::%s\n" % thing)
        return do(thing) or die(message)

    def pip_flags(flags=None):
        flags = dict(
            {
                '--download-cache': '/tmp/.cortex.pip_cache',
                '--build': '/tmp/.cortex.build',
                },
            **(flags or {}))
        return reduce(lambda acc, pair: acc + "%s=%s " % pair,
                      flags.items(),
                      "").strip()

    sys.stderr.write("=> Making env {name}\n".format(name=opts.name))
    do_or_die('virtualenv --no-site-packages {name}'.format(name=opts.name),
              "Failed to virtualenv")

    sys.stderr.write("=> Installing reqs\n")
    do_or_die('source {name}/bin/activate && pip install -E {name} {flags} -r requirements.txt'.format(name=opts.name,
                                                                                                       flags=pip_flags()),
              "Failed to install requirements")

    sys.stderr.write("=> Installing self\n")
    do_or_die('source {name}/bin/activate && python setup.py {arguments}'.format(name=opts.name,
                                                                          arguments=opts.develop and "develop" or
                                                                                    "install"),
              "Failed to install self")


    if options.get('exit', False): exit(0)

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--boot', '-b', dest="boot",
                      action="store_true",
                      default=False,
                      help="Bootstarp Cortex")
    parser.add_option('--name', '-n', dest="name",
                      default="node",
                      help="Name of environment to build [default: node]")
    parser.add_option("--permanent", '-p', dest="develop",
                      action='store_false',
                      default=True,
                      help="Install cortex as a library instead of for development (symlink here)")

    parser
    (options, args) = parser.parse_args()

    if options.boot: boot(options, *args, exit=True)

    setup(
        name='cortex',
        version='.1',
        description = 'playground for distributed computing',
        author      = 'mattvonrocketstein, in the gmails',
        url         = 'one of these days',

        package_dir = {'': 'lib'},
        packages    = find_packages('lib'),

        scripts     = [ 'data/_scripts/go',
                        'data/_scripts/go.py',
                        'data/_scripts/panic',
                        'data/_scripts/panic.py',]
    )

