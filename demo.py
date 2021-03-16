import sys
import pathlib
import os
import time


try:
    from pyrogen.src.pyrogen.version import __version__
    from pyrogen.src.pyrogen.tutorials.mainProgram import mainProgram
    from pyrogen.src.pyrogen.tutorials.scenes.simple_camera import SimpleCamera
    from pyrogen.src.pyrogen.tutorials.scenes.simple_gfx    import SimpleGfx
except ImportError:
    from pyrogen.version import __version__
    from pyrogen.tutorials.mainProgram import mainProgram
    from pyrogen.tutorials.scenes.simple_camera import SimpleCamera
    from pyrogen.tutorials.scenes.simple_gfx    import SimpleGfx



def runDemo(title):

    scenes = {
              "SimpleGfx"   : SimpleGfx,
              "SimpleCamera": SimpleCamera,
             }

    blankLine = "|                                                           |"
    ver     = f"| v{__version__}"
    verLine = ver + (len(blankLine) - len(ver) - 1) * " " + "|"

    print( "\n/===========================================================\\")
    print( "|   PPPP    Y   Y   RRRR     OOO     GGG    EEEEE   N   N   |")
    print( "|   P   P   Y   Y   R   R   O   O   G   G   E       N   N   |")
    print( "|   P   P    Y Y    R   R   O   O   G       E       N   N   |")
    print( "|   PPPP      Y     RRRR    O   O   G GGG   EEE     NN  N   |")
    print( "|   P         Y     R   R   O   O   G G G   E       N N N   |")
    print( "|   P         Y     R   R   O   O   G   G   E       N  NN   |")
    print( "|   P         Y     R   R    OOO     GGG    EEEEE   N   N   |")
    print( "|-----------------------------------------------------------|")
    print(verLine)

    if title in scenes:
        print( "|-----------------------------------------------------------|")
        sceneLine = f"| Running demo : '{title}'"
        print( sceneLine + (len(blankLine)-len(sceneLine)-1)*" " + "|" )
        print( "|-----------------------------------------------------------|")
        print( "| Press ESCAPE to exit                                      |")
        print( "| Press F11    to toggle screen mode (windowed/full)        |")
        print("\\===========================================================/\n", flush=True)

        mainProgram(title, scenes[title])

    else:
        print("\\===========================================================/\n", flush=True)
        msg  = f"\nThe demo name '{title}' does not exist.\n"
        msg += "To select and run a demo, please choose from following values : \n"
        for k in scenes.keys():
            msg += f"- '{k}'\n"
        time.sleep(1)
        raise RuntimeError(msg)



# Set current path to tutorials one
curPath = pathlib.Path(__file__).parent.absolute()
os.chdir(f"{curPath}/tutorials/")

# Get requested demo name
demoName = ""
if len(sys.argv)>1:
    demoName = sys.argv[1]

# Run demo
runDemo(demoName)

