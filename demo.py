import sys
import pathlib
import os
from .tutorials.rundemo import runDemo

if len(sys.argv)>1:

    curPath = pathlib.Path(__file__).parent.absolute()
    os.chdir(f"{curPath}/tutorials/")

    runDemo(sys.argv[1])

