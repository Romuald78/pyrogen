import sys
import pathlib
import os
# Import the tutorials (either from the dev branch or the standard package build)
try:
    from pyrogen.src.pyrogen.tutorials import rundemo
except:
    from pyrogen.tutorials import rundemo

# Set current path to tutorials one
curPath = pathlib.Path(__file__).parent.absolute()
os.chdir(f"{curPath}/tutorials/")

print("@")

# Get requested demo name
demoName = ""
if len(sys.argv)>1:
    demoName = sys.argv[1]

# Run demo
rundemo.runDemo(demoName)

