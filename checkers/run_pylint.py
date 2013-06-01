# coding: utf-8
import os
import sys
import subprocess

CHECKERS_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.dirname(CHECKERS_DIR))

rcfile = os.path.join(CHECKERS_DIR, 'pylint.conf')
output = os.path.join(CHECKERS_DIR, 'pylint.html')


modules = []
# for dir in os.listdir()

cmd = ['pylint',
       '--output-format', 'html',
       '--include-ids', 'y',
       '--rcfile', rcfile,
       'the_tale']

print cmd
with open(output, 'w') as f:
    # codecs.getwriter(locale.getpreferredencoding())(f)
    subprocess.call(cmd, stdout=f, stderr=sys.stderr)
