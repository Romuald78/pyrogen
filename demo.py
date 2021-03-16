import sys

from .tutorials.rundemo import runDemo

if len(sys.argv)>1:
    runDemo(sys.argv[1])

