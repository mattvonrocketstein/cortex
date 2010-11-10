#!/usr/bin/env python

from distutils.core import setup
#package_dir = {'': 'lib'}
setup(name='cortex',
      version='.1',
      description = 'playground for distributed computing',
      author      = 'mattvonrocketstein, in the gmails',
      url         = 'one of these days',
      packages    = ['cortex'],
      scripts     = [ 'data/_scripts/go',
                      'data/_scripts/go.py', ]
     )
